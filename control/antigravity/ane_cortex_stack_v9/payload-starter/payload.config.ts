import { buildConfig } from 'payload/config';
import BenchmarkReports from './src/collections/BenchmarkReports';
import SemanticMemories from './src/collections/SemanticMemories';

export default buildConfig({
  collections: [BenchmarkReports, SemanticMemories],
});
