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

test.describe('Admin editorial workflow', () => {
  test('allows an editor-in-chief to publish and unpublish a reviewed post', async ({ page }) => {
    const uniqueId = Date.now()
    const title = `Workflow Admin ${uniqueId}`

    await loginViaKeycloak(page)
    await expect(page.getByRole('heading', { name: 'Nova Publicação' })).toBeVisible()

    await page.fill('#title', title)
    await page.fill('#subtitle', 'Cobertura do workflow editorial')

    const editor = page.locator('.ProseMirror').first()
    await editor.click()
    await editor.pressSequentially('Conteudo suficiente para validar transicoes editoriais.')

    await page.selectOption('#status', 'REVIEW')
    await page.locator('input[id^="category-"]').first().check({ timeout: 30_000 })

    await Promise.all([
      page.waitForURL('**/admin/posts'),
      page.getByRole('button', { name: 'Salvar Publicação' }).click(),
    ])

    const createdRow = page.getByRole('row', { name: new RegExp(`${title}.*Em revisão`) })
    await expect(createdRow).toBeVisible()

    await createdRow.getByRole('link', { name: 'Editar' }).click()
    await page.waitForURL('**/admin/posts/*/edit')

    await page.selectOption('#status', 'PUBLISHED')
    await expect(page.locator('#published_at')).toBeVisible()

    await Promise.all([
      page.waitForURL('**/admin/posts'),
      page.getByRole('button', { name: 'Salvar Alterações' }).click(),
    ])

    const publishedRow = page.getByRole('row', { name: new RegExp(`${title}.*Publicado`) })
    await expect(publishedRow).toBeVisible()
    await expect(publishedRow).not.toContainText(' - ')

    await publishedRow.getByRole('link', { name: 'Editar' }).click()
    await page.waitForURL('**/admin/posts/*/edit')

    await page.selectOption('#status', 'DRAFT')
    await expect(page.locator('#published_at')).toHaveCount(0)

    await Promise.all([
      page.waitForURL('**/admin/posts'),
      page.getByRole('button', { name: 'Salvar Alterações' }).click(),
    ])

    const draftRow = page.getByRole('row', { name: new RegExp(`${title}.*Rascunho`) })
    await expect(draftRow).toBeVisible()
    await expect(draftRow).toContainText('Rascunho')
  })
})
