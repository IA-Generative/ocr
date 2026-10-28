import antfu from '@antfu/eslint-config'

/**
 * Repository-level lint rules: compose files, CI workflows, docs and root
 * tooling config.
 *
 * `apps/client` is deliberately excluded — it ships its own flat config, tuned
 * for Vue/TypeScript, and installs its own ESLint. `apps/server` and `sdk` are
 * Python and are covered by ruff (`make lint-backend`).
 */
export default antfu(
  {
    // No source code lives at this level.
    typescript: false,
    vue: false,
    jsonc: true,
    markdown: true,
    yaml: true,
    ignores: [
      '**/node_modules',
      '**/pnpm-lock.yaml',
      '**/uv.lock',
      '**/.venv',
      '**/dist/',
      '**/coverage/',
      // Owned by apps/client/eslint.config.js.
      'apps/**',
      // sdk/ (Python, linted by ruff) and sdk/js/ (TypeScript, ships its own flat
      // config and installs its own ESLint - same pattern as apps/client above).
      'sdk/**',
      // Helm charts and Kubernetes manifests: Go templates are not parseable as
      // YAML, and the value files are validated by `helm lint` / chart-testing
      // in CI rather than by a JS style linter.
      'helm/**',
      // Not a format ESLint understands.
      '**/*.toml',
      // Generated.
      '**/CHANGELOG.md',
      '.ruff_cache/**',
      '**/*.md/*.js',
      '**/*.md/*.ts',
    ],
    stylistic: {
      overrides: {
        'style/comma-dangle': ['error', 'always-multiline'],
        'style/quote-props': [
          'error',
          'as-needed',
          { keywords: false, unnecessary: true },
        ],
        'style/brace-style': [
          'error',
          '1tbs',
          { allowSingleLine: true },
        ],
        'style/space-before-function-paren': ['error', 'always'],
      },
    },
  },
  {
    // Prose is written in French, where a narrow no-break space before `?`,
    // `:` and `»` is correct typography rather than a mistake.
    name: 'ocr/markdown',
    files: ['**/*.md'],
    rules: {
      'no-irregular-whitespace': 'off',
    },
  },
  {
    name: 'ocr/root-rules',
    rules: {
      'antfu/if-newline': 'off',
      curly: ['error', 'all'],
      'jsonc/sort-keys': 'off',
      'unused-imports/no-unused-imports': 'error',
    },
  },
  {
    name: 'ocr/yaml',
    files: ['**/*.{yml,yaml}'],
    rules: {
      // Quoting in these files is load-bearing, not stylistic: `"3.13"` must
      // stay a string or a Python version silently becomes the float 3.13.
      'yaml/plain-scalar': 'off',
      'yaml/quotes': 'off',
      // Compose files indent block sequences, GitHub workflows do not, and both
      // are idiomatic. `.editorconfig` already pins the indent width.
      'yaml/indent': 'off',
      // Double spaces before a trailing comment are how pinned action SHAs are
      // annotated with their tag (`uses: actions/checkout@sha  # v6.1.0`).
      'style/no-multi-spaces': 'off',
    },
  },
).override('antfu/node/rules', {
  rules: {
    'node/prefer-global/process': ['error', 'always'],
    'node/prefer-global/console': ['error', 'always'],
    'node/prefer-global/buffer': ['error', 'always'],
  },
})
