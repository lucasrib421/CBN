'use client'

import Link from '@tiptap/extension-link'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/react'
import { useEffect } from 'react'

import { sanitizeRichTextHtml } from '@/lib/rich-text-policy'

type PostRichTextEditorProps = {
  value?: string
  onChange: (value: string) => void
  onBlur?: () => void
  error?: string
}

const LINK_PROTOCOL_PATTERN = /^(https?:|mailto:)/i

function ToolbarButton({
  label,
  isActive,
  onClick,
  disabled,
}: {
  label: string
  isActive?: boolean
  onClick: () => void
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`rounded px-2 py-1 text-sm transition-colors ${
        isActive ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
      } disabled:cursor-not-allowed disabled:opacity-50`}
    >
      {label}
    </button>
  )
}

export default function PostRichTextEditor({
  value,
  onChange,
  onBlur,
  error,
}: PostRichTextEditorProps) {
  const normalizedValue = value || '<p></p>'

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [2, 3],
        },
        code: false,
        codeBlock: false,
        strike: false,
      }),
      Link.configure({
        openOnClick: false,
        autolink: true,
        protocols: ['http', 'https', 'mailto'],
      }),
    ],
    content: normalizedValue,
    editorProps: {
      attributes: {
        class:
          'min-h-64 max-h-[28rem] overflow-y-auto rounded-b border-0 p-4 prose prose-sm max-w-none focus:outline-none',
      },
      transformPastedHTML: (html) => sanitizeRichTextHtml(html),
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    onBlur: () => onBlur?.(),
  })

  useEffect(() => {
    if (!editor) return
    if (editor.getHTML() === normalizedValue) return
    editor.commands.setContent(normalizedValue, { emitUpdate: false })
  }, [editor, normalizedValue])

  const handleLink = () => {
    if (!editor) return

    const currentLink = editor.getAttributes('link').href as string | undefined
    const input = window.prompt('Informe a URL do link', currentLink || 'https://')
    if (input === null) return

    const nextValue = input.trim()
    if (nextValue.length === 0) {
      editor.chain().focus().unsetLink().run()
      return
    }

    if (!LINK_PROTOCOL_PATTERN.test(nextValue)) {
      return
    }

    editor
      .chain()
      .focus()
      .setLink({
        href: nextValue,
        target: '_blank',
        rel: 'noopener noreferrer',
      })
      .run()
  }

  return (
    <div className="space-y-3">
      <div className="rounded-md border border-gray-300">
        <div className="flex flex-wrap gap-2 border-b border-gray-200 bg-gray-50 p-2">
          <ToolbarButton
            label="H2"
            isActive={editor?.isActive('heading', { level: 2 })}
            onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
            disabled={!editor?.can().chain().focus().toggleHeading({ level: 2 }).run()}
          />
          <ToolbarButton
            label="H3"
            isActive={editor?.isActive('heading', { level: 3 })}
            onClick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()}
            disabled={!editor?.can().chain().focus().toggleHeading({ level: 3 }).run()}
          />
          <ToolbarButton
            label="Negrito"
            isActive={editor?.isActive('bold')}
            onClick={() => editor?.chain().focus().toggleBold().run()}
            disabled={!editor?.can().chain().focus().toggleBold().run()}
          />
          <ToolbarButton
            label="Itálico"
            isActive={editor?.isActive('italic')}
            onClick={() => editor?.chain().focus().toggleItalic().run()}
            disabled={!editor?.can().chain().focus().toggleItalic().run()}
          />
          <ToolbarButton
            label="Lista UL"
            isActive={editor?.isActive('bulletList')}
            onClick={() => editor?.chain().focus().toggleBulletList().run()}
            disabled={!editor?.can().chain().focus().toggleBulletList().run()}
          />
          <ToolbarButton
            label="Lista OL"
            isActive={editor?.isActive('orderedList')}
            onClick={() => editor?.chain().focus().toggleOrderedList().run()}
            disabled={!editor?.can().chain().focus().toggleOrderedList().run()}
          />
          <ToolbarButton
            label="Citação"
            isActive={editor?.isActive('blockquote')}
            onClick={() => editor?.chain().focus().toggleBlockquote().run()}
            disabled={!editor?.can().chain().focus().toggleBlockquote().run()}
          />
          <ToolbarButton
            label="Link"
            isActive={editor?.isActive('link')}
            onClick={handleLink}
            disabled={!editor}
          />
          <ToolbarButton
            label="Remover link"
            onClick={() => editor?.chain().focus().unsetLink().run()}
            disabled={!editor?.isActive('link')}
          />
          <ToolbarButton
            label="Separador"
            onClick={() => editor?.chain().focus().setHorizontalRule().run()}
            disabled={!editor?.can().chain().focus().setHorizontalRule().run()}
          />
        </div>
        <EditorContent editor={editor} />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div>
        <p className="mb-2 text-sm font-medium text-gray-700">Preview</p>
        <div
          data-testid="post-rich-text-preview"
          className="prose prose-sm max-w-none rounded-md border border-gray-200 bg-gray-50 p-4"
          dangerouslySetInnerHTML={{ __html: sanitizeRichTextHtml(normalizedValue) }}
        />
      </div>
    </div>
  )
}
