const RULES: [RegExp, string][] = [
  [/\bdocker\s+system\s+prune\b/, 'docker system prune removes unused containers, networks and images'],
  [/\bdocker\s+volume\s+(rm|prune)\b/, 'docker volume removal can delete container data'],
  [/\bdocker\s+(rm|container\s+rm)\b[^|;&]*\s-\w*v/, 'docker rm -v deletes volumes'],
  [/\brm\s+(-\w*[rf]\w*\s+)+[^|;&]*\/volume\w*\//, 'rm -r/-f under a /volume path'],
  [/\brm\s+(-\w*[rf]\w*\s+)+(\/|~|\$HOME)(\s|$)/, 'rm -r/-f on / or home'],
  [/\bfind\b[^|;&]*\/volume\w*\/[^|;&]*-delete\b/, 'find -delete under a /volume path'],
  [/\bmkfs\b|\bdd\s+[^|;&]*of=\/dev\//, 'writes to a disk device'],
]

export function check(command: string): string | undefined {
  if (/#recycle/.test(command) && /\b(mv|rsync)\b/.test(command)) return undefined
  for (const [re, why] of RULES) if (re.test(command)) return why
  return undefined
}
