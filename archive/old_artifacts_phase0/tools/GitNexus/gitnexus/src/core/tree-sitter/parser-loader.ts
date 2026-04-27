import { createRequire } from 'node:module';
import Parser from 'tree-sitter';
import C from 'tree-sitter-c';
import CSharp from 'tree-sitter-c-sharp';
import CPP from 'tree-sitter-cpp';
import Go from 'tree-sitter-go';
import Java from 'tree-sitter-java';
import JavaScript from 'tree-sitter-javascript';
import PHP from 'tree-sitter-php';
import Python from 'tree-sitter-python';
import Ruby from 'tree-sitter-ruby';
import Rust from 'tree-sitter-rust';
import TypeScript from 'tree-sitter-typescript';
import { SupportedLanguages } from '../../config/supported-languages.js';

// tree-sitter-swift and tree-sitter-dart are optionalDependencies — may not be installed
const _require = createRequire(import.meta.url);
let Swift: any = null;
try {
  Swift = _require('tree-sitter-swift');
} catch {}
let Dart: any = null;
try {
  Dart = _require('tree-sitter-dart');
} catch {}

// tree-sitter-kotlin is an optionalDependency — may not be installed
let Kotlin: any = null;
try {
  Kotlin = _require('tree-sitter-kotlin');
} catch {}

let parser: Parser | null = null;

const languageMap: Record<string, any> = {
  [SupportedLanguages.JavaScript]: JavaScript,
  [SupportedLanguages.TypeScript]: TypeScript.typescript,
  [`${SupportedLanguages.TypeScript}:tsx`]: TypeScript.tsx,
  [SupportedLanguages.Python]: Python,
  [SupportedLanguages.Java]: Java,
  [SupportedLanguages.C]: C,
  [SupportedLanguages.CPlusPlus]: CPP,
  [SupportedLanguages.CSharp]: CSharp,
  [SupportedLanguages.Go]: Go,
  [SupportedLanguages.Rust]: Rust,
  ...(Kotlin ? { [SupportedLanguages.Kotlin]: Kotlin } : {}),
  [SupportedLanguages.PHP]: PHP.php_only,
  [SupportedLanguages.Ruby]: Ruby,
  ...(Dart ? { [SupportedLanguages.Dart]: Dart } : {}),
  ...(Swift ? { [SupportedLanguages.Swift]: Swift } : {}),
};

export const isLanguageAvailable = (language: SupportedLanguages): boolean =>
  language in languageMap;

export const loadParser = async (): Promise<Parser> => {
  if (parser) return parser;
  parser = new Parser();
  return parser;
};

export const loadLanguage = async (
  language: SupportedLanguages,
  filePath?: string,
): Promise<void> => {
  if (!parser) await loadParser();
  const key =
    language === SupportedLanguages.TypeScript && filePath?.endsWith('.tsx')
      ? `${language}:tsx`
      : language;

  const lang = languageMap[key];
  if (!lang) {
    throw new Error(`Unsupported language: ${language}`);
  }
  parser!.setLanguage(lang);
};
