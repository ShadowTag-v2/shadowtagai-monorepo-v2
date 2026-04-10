import {defineConfig} from 'rollup';
import {dts} from 'rollup-plugin-dts'
import esbuild from 'rollup-plugin-esbuild'

type Extension = 'cjs'|'d.ts'|'mjs';

const bundle =
    (ext: Extension) => {
      const file = `dist/index.${ext}`;

      return defineConfig({
        input: 'src/index.ts',

        output: {
          file,

          sourcemap: false,
          format: ext === 'cjs' ? 'cjs' : 'esm',
          exports: 'named'
        },

        plugins: ext == 'd.ts' ? [dts()] : [esbuild({target: 'es2020'})],

        external: id => !/^[./]/.test(id),
      })
    }

export default [
  bundle('cjs'),
  bundle('d.ts'),
  bundle('mjs'),
]
