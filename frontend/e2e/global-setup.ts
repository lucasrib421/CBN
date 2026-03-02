import { execSync } from 'node:child_process'
import path from 'node:path'

async function waitForUrl(url: string, timeoutMs = 180_000): Promise<void> {
  const deadline = Date.now() + timeoutMs
  let lastError: unknown = null
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url)
      if (response.ok) {
        return
      }
      lastError = `Unexpected status ${response.status}`
    } catch (error) {
      lastError = error
    }
    await new Promise((resolve) => setTimeout(resolve, 1_000))
  }
  throw new Error(`Timeout while waiting for ${url}. Last error: ${String(lastError)}`)
}

export default async function globalSetup(): Promise<void> {
  const repoRoot = path.resolve(__dirname, '../..')
  const composeUpCmd =
    process.env.E2E_SKIP_BUILD === '1'
      ? 'docker compose up -d -V db redis keycloak api frontend'
      : 'docker compose up -d --build -V db redis keycloak api frontend'

  execSync(composeUpCmd, {
    cwd: repoRoot,
    stdio: 'inherit',
  })

  await waitForUrl('http://localhost:8080/realms/master/.well-known/openid-configuration')
  await waitForUrl('http://localhost:8000/api/v1/posts/')
  await waitForUrl('http://localhost:3000')

  execSync('.venv-pr/bin/python scripts/e2e_seed.py', {
    cwd: repoRoot,
    stdio: 'inherit',
    env: {
      ...process.env,
      POSTGRES_HOST: 'localhost',
      POSTGRES_PORT: '5433',
      REDIS_URL: 'redis://localhost:6379/1',
    },
  })
}
