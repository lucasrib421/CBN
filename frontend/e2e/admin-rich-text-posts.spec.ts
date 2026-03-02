import { expect, test } from '@playwright/test'

const E2E_EDITOR_USERNAME = process.env.E2E_EDITOR_USERNAME || 'e2e_editor'
const E2E_EDITOR_PASSWORD = process.env.E2E_EDITOR_PASSWORD || 'e2e-editor-123'
const E2E_KEYCLOAK_REALM = process.env.E2E_KEYCLOAK_REALM || process.env.AUTH_KEYCLOAK_REALM
const KEYCLOAK_AUTH_PATH_RE = /\/realms\/[^/]+\/protocol\/openid-connect\/auth/

function isKeycloakAuthUrl(url: string): boolean {
  if (E2E_KEYCLOAK_REALM) {
    return url.includes(`/realms/${E2E_KEYCLOAK_REALM}/protocol/openid-connect/auth`)
  }
  return KEYCLOAK_AUTH_PATH_RE.test(url)
}

async function loginViaKeycloak(page: import('@playwright/test').Page): Promise<void> {
  await page.goto('/api/auth/signin?callbackUrl=/admin/posts/new')

  if (page.url().includes('/api/auth/signin')) {
    const providerButton = page
      .getByRole('button', { name: /keycloak/i })
      .or(page.getByRole('link', { name: /keycloak/i }))
      .first()
    await providerButton.click()
  }

  if (isKeycloakAuthUrl(page.url())) {
    await page.locator('input[name="username"]').fill(E2E_EDITOR_USERNAME)
    await page.locator('input[name="password"]').fill(E2E_EDITOR_PASSWORD)
    await page.locator('#kc-login').click()
  }

  await page.waitForURL('**/admin/posts/new')
}

test.describe('Admin posts rich text flow', () => {
  test('creates and edits a post with rich text editor in real browser flow', async ({ page }) => {
    const uniqueId = Date.now()
    const initialTitle = `E2E Post ${uniqueId}`
    const updatedTitle = `${initialTitle} Atualizado`
    let createdPostId: number | null = null

    await loginViaKeycloak(page)
    const session = (await page.evaluate(async () => {
      const response = await fetch('/api/auth/session', { credentials: 'include' })
      return response.json()
    })) as { accessToken?: string } | null
    expect(session?.accessToken).toBeTruthy()

    await page.goto('/admin/posts/new')
    await expect(page.getByRole('heading', { name: 'Nova Publicação' })).toBeVisible()

    await page.fill('#title', initialTitle)
    await page.fill('#subtitle', 'Subtítulo E2E')

    const editor = page.locator('.ProseMirror').first()
    await editor.click()
    await editor.pressSequentially('Titulo do teste E2E')
    await page.keyboard.press('Enter')
    await editor.pressSequentially('Paragrafo principal com texto suficiente para leitura.')

    await page.getByRole('button', { name: 'Negrito' }).click()
    await editor.pressSequentially(' Trecho em negrito')
    await page.getByRole('button', { name: 'Lista UL' }).click()
    await editor.pressSequentially(' Item de lista')

    const preview = page.getByTestId('post-rich-text-preview')
    await expect(preview).toContainText('Titulo do teste E2E')
    await expect(preview).toContainText('Paragrafo principal')

    await page.locator('input[id^="category-"]').first().check({ timeout: 30_000 })

    await page.route('**/api/v1/painel/posts/', async (route) => {
      if (route.request().method() !== 'POST') {
        await route.continue()
        return
      }
      const body = route.request().postDataJSON() as Record<string, unknown>
      const originalContent = String(body.content || '')
      body.content = `${originalContent}<script>alert("xss")</script><a href="javascript:alert(1)">X</a>`
      await route.continue({ postData: JSON.stringify(body) })
    })

    const createResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/api/v1/painel/posts/') && response.request().method() === 'POST',
      { timeout: 30_000 },
    )

    await page.getByRole('button', { name: 'Salvar Publicação' }).click()
    const createResponse = await createResponsePromise

    if (!createResponse.ok()) {
      throw new Error(
        `Create response failed (${createResponse.status()}): ${await createResponse.text()}`,
      )
    }
    const createPayload = (await createResponse.json()) as { id: number }
    createdPostId = createPayload.id
    expect(createdPostId).toBeGreaterThan(0)

    await page.waitForURL('**/admin/posts')

    await expect(page.getByText(initialTitle)).toBeVisible()

    const createdPost = (await page.evaluate(
      async ({ token, id }) => {
        const response = await fetch(`http://localhost:8000/api/v1/painel/posts/${id}/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        return {
          ok: response.ok,
          status: response.status,
          data: await response.json(),
        }
      },
      { token: session?.accessToken as string, id: createdPostId },
    )) as { ok: boolean; status: number; data: { content: string; reading_time: number | null } }
    expect(createdPost.ok).toBeTruthy()
    expect(createdPost.data.content).not.toContain('<script')
    expect(createdPost.data.content).not.toContain('javascript:')
    expect(createdPost.data.reading_time).not.toBeNull()

    await page.getByRole('link', { name: 'Editar' }).first().click()
    await page.waitForURL(`**/admin/posts/${createdPostId}/edit`)
    await expect(page.getByRole('heading', { name: 'Editar Publicação' })).toBeVisible()

    await page.fill('#title', updatedTitle)
    const editEditor = page.locator('.ProseMirror').first()
    await editEditor.click()
    await editEditor.pressSequentially(' Conteudo atualizado no E2E.')

    const updateResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes(`/api/v1/painel/posts/${createdPostId}/`) &&
        response.request().method() === 'PUT',
    )

    await page.getByRole('button', { name: 'Salvar Alterações' }).click()
    await page.waitForURL('**/admin/posts')
    const updateResponse = await updateResponsePromise
    expect(updateResponse.ok()).toBeTruthy()

    await expect(page.getByText(updatedTitle)).toBeVisible()

    const updatedPost = (await page.evaluate(
      async ({ token, id }) => {
        const response = await fetch(`http://localhost:8000/api/v1/painel/posts/${id}/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        return {
          ok: response.ok,
          status: response.status,
          data: await response.json(),
        }
      },
      { token: session?.accessToken as string, id: createdPostId },
    )) as { ok: boolean; status: number; data: { title: string; content: string } }
    expect(updatedPost.ok).toBeTruthy()
    expect(updatedPost.data.title).toBe(updatedTitle)
    expect(updatedPost.data.content).toContain('Conteudo atualizado no E2E')
  })
})
