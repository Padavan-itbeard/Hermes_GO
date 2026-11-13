#!/usr/bin/env node
// Открыть файл карточек Гермеса в Ivy: node ivy/show.js anki/<файл>.json
// Вся механика — в open.js, общем для Гермеса, Афины и Хирона.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { openCards } from './open.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
await openCards({
  anki: path.resolve(HERE, '..', 'anki'),
  ivyDir: HERE,
  agent: 'Hermes',
  dryEnv: 'HERMES_IVY_DRY',
});
