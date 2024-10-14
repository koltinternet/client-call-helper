import path from 'path';

const root_dir = import.meta.dirname;

console.log(root_dir);

console.log(path.resolve(root_dir, '..'));