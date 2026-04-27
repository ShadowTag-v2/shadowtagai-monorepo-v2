import { Repo } from './repo';
import { User } from './user';

export function processEntities(): void {
  const user = new User();
  const repo = new Repo();
  user.save();
  repo.save();
}
