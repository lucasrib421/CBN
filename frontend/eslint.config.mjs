import { createRequire } from 'node:module'
import js from '@eslint/js'
import nextConfig from 'eslint-config-next/core-web-vitals'

const require = createRequire(import.meta.url)
const eslintVersion = require('eslint/package.json').version
const eslintMajor = Number.parseInt(eslintVersion.split('.')[0] ?? '0', 10)
const useNextConfig = Number.isFinite(eslintMajor) && eslintMajor < 10

const eslintConfig = [
  {
    ignores: ['.next/**', 'node_modules/**', 'out/**'],
  },
  js.configs.recommended,
  ...(useNextConfig ? nextConfig : []),
  ...(useNextConfig
    ? [
        {
          rules: {
            '@next/next/no-img-element': 'off',
          },
        },
      ]
    : []),
]

export default eslintConfig
