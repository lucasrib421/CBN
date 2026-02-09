import nextConfig from 'eslint-config-next/core-web-vitals'

const eslintConfig = [
  {
    ignores: ['.next/**', 'node_modules/**', 'out/**'],
  },
  ...nextConfig,
  {
    rules: {
      '@next/next/no-img-element': 'off',
    },
  },
]

export default eslintConfig
