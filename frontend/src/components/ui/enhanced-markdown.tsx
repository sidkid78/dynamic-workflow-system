// components/ui/enhanced-markdown.tsx
import React from 'react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

interface EnhancedMarkdownProps {
  content: string;
  className?: string;
}

const EnhancedMarkdown: React.FC<EnhancedMarkdownProps> = ({ content, className = '' }) => {
  return (
    <div className={`prose dark:prose-invert max-w-none ${className} dark:[&_*]:!text-gray-200`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, [rehypeHighlight, { ignoreMissing: true }]]}
        components={{
          table({ children, ...props }) {
            return (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 border border-gray-200 dark:border-gray-700 rounded-md dark:bg-gray-800/30" {...props}>
                  {children}
                </table>
              </div>
            );
          },
          thead({ children, ...props }) {
            return (
              <thead className="bg-gray-50 dark:bg-gray-800/50" {...props}>
                {children}
              </thead>
            );
          },
          tbody({ children, ...props }) {
            return (
              <tbody className="bg-white dark:bg-gray-900/20 divide-y divide-gray-200 dark:divide-gray-700" {...props}>
                {children}
              </tbody>
            );
          },
          tr({ children, ...props }) {
            return (
              <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/30" {...props}>
                {children}
              </tr>
            );
          },
          th({ children, ...props }) {
            return (
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider" {...props}>
                {children}
              </th>
            );
          },
          td({ children, ...props }) {
            return (
              <td className="px-6 py-4 whitespace-normal text-sm text-gray-700 dark:text-gray-300" {...props}>
                {children}
              </td>
            );
          },
          p({ children, ...props }) {
            return (
              <p className="mb-4 leading-relaxed dark:text-gray-300" {...props}>
                {children}
              </p>
            );
          },
          ul({ children, ...props }) {
            return (
              <ul className="list-disc pl-6 mb-4 space-y-1 dark:text-gray-300" {...props}>
                {children}
              </ul>
            );
          },
          ol({ children, ...props }) {
            return (
              <ol className="list-decimal pl-6 mb-4 space-y-1 dark:text-gray-300" {...props}>
                {children}
              </ol>
            );
          },
          h1({ children, ...props }) {
            return (
              <h1 className="text-2xl font-bold mt-6 mb-4 border-b pb-2 dark:border-gray-700 dark:text-gray-100" {...props}>
                {children}
              </h1>
            );
          },
          h2({ children, ...props }) {
            return (
              <h2 className="text-xl font-semibold mt-5 mb-3 border-b pb-1 dark:border-gray-700 dark:text-gray-100" {...props}>
                {children}
              </h2>
            );
          },
          h3({ children, ...props }) {
            return (
              <h3 className="text-lg font-medium mt-4 mb-2 dark:text-gray-100" {...props}>
                {children}
              </h3>
            );
          },
          h4({ children, ...props }) {
            return (
              <h4 className="text-base font-medium mt-3 mb-2 dark:text-gray-100" {...props}>
                {children}
              </h4>
            );
          },
          blockquote({ children, ...props }) {
            return (
              <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-700 dark:text-gray-400 my-4 bg-gray-50 dark:bg-gray-800/30" {...props}>
                {children}
              </blockquote>
            );
          },
          a({ children, href, ...props }) {
            return (
              <a 
                href={href} 
                className="text-blue-600 hover:underline dark:text-blue-400 dark:hover:text-blue-300"
                target={href?.startsWith('http') ? "_blank" : undefined}
                rel={href?.startsWith('http') ? "noopener noreferrer" : undefined}
                {...props}
              >
                {children}
              </a>
            );
          },
          img({ alt, src, ...props }) {
            if (typeof src !== 'string') {
              return null;
            }
            const { width: propWidth, height: propHeight, ...restProps } = props;
            const imageWidth = typeof propWidth === 'number' ? propWidth : 800; 
            const imageHeight = typeof propHeight === 'number' ? propHeight : 400;
            return (
              <Image 
                src={src}
                alt={alt || ''} 
                width={imageWidth}
                height={imageHeight}
                className="max-w-full h-auto rounded my-4 shadow-md dark:shadow-gray-900/50"
                style={{ height: 'auto' }}
                {...restProps}
              />
            );
          },
          hr({ ...props }) {
            return (
              <hr className="my-6 border-t border-gray-300 dark:border-gray-700" {...props} />
            );
          },
          code({ children, ...props }) {
            return (
              <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            );
          },
          pre({ children, ...props }) {
            return (
              <pre className="bg-gray-900 dark:bg-gray-800/50 rounded-lg p-4 my-4 overflow-x-auto" {...props}>
                {children}
              </pre>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default EnhancedMarkdown;