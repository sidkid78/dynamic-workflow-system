declare module 'react-syntax-highlighter/dist/esm/prism' {
  import { ComponentType } from 'react';
  
  interface StyleDefinition {
    'code[class*="language-"]'?: {
      color?: string;
      backgroundColor?: string;
      [key: string]: string | undefined;
    };
    [key: string]: any;
  }

  interface SyntaxHighlighterProps {
    children: string;
    style: StyleDefinition;
    language?: string;
    PreTag?: string;
  }

  export const Prism: ComponentType<SyntaxHighlighterProps>;
} 