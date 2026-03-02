import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, test, vi } from 'vitest'

type ChainMock = {
  focus: ReturnType<typeof vi.fn>
  toggleBold: ReturnType<typeof vi.fn>
  toggleHeading: ReturnType<typeof vi.fn>
  toggleItalic: ReturnType<typeof vi.fn>
  toggleBulletList: ReturnType<typeof vi.fn>
  toggleOrderedList: ReturnType<typeof vi.fn>
  toggleBlockquote: ReturnType<typeof vi.fn>
  setHorizontalRule: ReturnType<typeof vi.fn>
  unsetLink: ReturnType<typeof vi.fn>
  setLink: ReturnType<typeof vi.fn>
  run: ReturnType<typeof vi.fn>
}

const buildChainMock = (): ChainMock => {
  const chain = {} as ChainMock
  chain.focus = vi.fn(() => chain)
  chain.toggleBold = vi.fn(() => chain)
  chain.toggleHeading = vi.fn(() => chain)
  chain.toggleItalic = vi.fn(() => chain)
  chain.toggleBulletList = vi.fn(() => chain)
  chain.toggleOrderedList = vi.fn(() => chain)
  chain.toggleBlockquote = vi.fn(() => chain)
  chain.setHorizontalRule = vi.fn(() => chain)
  chain.unsetLink = vi.fn(() => chain)
  chain.setLink = vi.fn(() => chain)
  chain.run = vi.fn(() => true)
  return chain
}

const commandChain = buildChainMock()
const canChain = buildChainMock()

const mockEditor = {
  chain: vi.fn(() => commandChain),
  can: vi.fn(() => ({ chain: () => canChain })),
  commands: {
    setContent: vi.fn(),
  },
  isActive: vi.fn(() => false),
  getAttributes: vi.fn(() => ({})),
  getHTML: vi.fn(() => '<p></p>'),
}

vi.mock('@tiptap/react', () => ({
  EditorContent: ({ editor }: { editor: unknown }) => (
    <div data-testid="mock-editor-content">{editor ? 'editor-ready' : 'editor-missing'}</div>
  ),
  useEditor: vi.fn(() => mockEditor),
}))

vi.mock('@tiptap/starter-kit', () => ({
  default: {
    configure: vi.fn(() => ({ name: 'starter-kit' })),
  },
}))

vi.mock('@tiptap/extension-link', () => ({
  default: {
    configure: vi.fn(() => ({ name: 'link' })),
  },
}))

import PostRichTextEditor from './PostRichTextEditor'

describe('PostRichTextEditor', () => {
  beforeEach(() => {
    commandChain.toggleBold.mockClear()
    commandChain.setLink.mockClear()
    commandChain.unsetLink.mockClear()
    mockEditor.isActive.mockClear()
  })

  test('renders sanitized preview content', () => {
    render(
      <PostRichTextEditor
        value="<p>Texto</p><script>alert(1)</script>"
        onChange={vi.fn()}
      />,
    )

    const preview = screen.getByTestId('post-rich-text-preview')
    expect(preview.innerHTML).toContain('<p>Texto</p>')
    expect(preview.innerHTML).not.toContain('<script')
  })

  test('executes bold command when toolbar button is clicked', () => {
    render(<PostRichTextEditor value="<p>Texto</p>" onChange={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Negrito' }))

    expect(commandChain.focus).toHaveBeenCalled()
    expect(commandChain.toggleBold).toHaveBeenCalled()
    expect(commandChain.run).toHaveBeenCalled()
  })

  test('creates link from toolbar prompt', () => {
    const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('https://cbn.com')

    render(<PostRichTextEditor value="<p>Texto</p>" onChange={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Link' }))

    expect(commandChain.setLink).toHaveBeenCalledWith({
      href: 'https://cbn.com',
      rel: 'noopener noreferrer',
      target: '_blank',
    })

    promptSpy.mockRestore()
  })

  test('accepts internal links from toolbar prompt', () => {
    const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('/categoria/politica')

    render(<PostRichTextEditor value="<p>Texto</p>" onChange={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Link' }))

    expect(commandChain.setLink).toHaveBeenCalledWith({
      href: '/categoria/politica',
      rel: 'noopener noreferrer',
      target: '_blank',
    })

    promptSpy.mockRestore()
  })

  test('ignores unsupported link protocols from toolbar prompt', () => {
    const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('javascript:alert(1)')

    render(<PostRichTextEditor value="<p>Texto</p>" onChange={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: 'Link' }))

    expect(commandChain.setLink).not.toHaveBeenCalled()
    expect(commandChain.unsetLink).not.toHaveBeenCalled()

    promptSpy.mockRestore()
  })
})
