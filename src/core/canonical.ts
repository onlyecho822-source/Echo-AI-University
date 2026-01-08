import { createHash } from 'crypto';

/**
 * Canonical JSON serialization (RFC 8785 minimal implementation)
 * Ensures same semantic content → same byte string across all platforms
 */
export function canonicalize(value: any): string {
  if (value === null || typeof value !== 'object') {
    // Primitives: use standard JSON
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    const items = value.map(item => canonicalize(item));
    return `[${items.join(',')}]`;
  }

  // Object: sort keys lexicographically
  const keys = Object.keys(value).sort();
  const entries = keys.map(key => {
    const canonicalKey = canonicalize(key);
    const canonicalValue = canonicalize(value[key]);
    return `${canonicalKey}:${canonicalValue}`;
  });

  return `{${entries.join(',')}}`;
}

/**
 * SHA-256 hash of canonicalized input
 */
export function sha256Hex(input: any): string {
  const canonical = canonicalize(input);
  return createHash('sha256').update(canonical).digest('hex');
}

/**
 * Generate deterministic ID matching schema pattern: prefix_32hex
 */
export function id32(prefix: string, material: string): string {
  return `${prefix}_${sha256Hex(material).slice(0, 32)}`;
}

/**
 * Deep freeze for immutability enforcement
 */
export function deepFreeze<T>(obj: T): T {
  if (obj && typeof obj === 'object') {
    Object.freeze(obj);
    for (const key of Object.keys(obj as any)) {
      deepFreeze((obj as any)[key]);
    }
  }
  return obj;
}

/**
 * Clone without freezing (for safe returns)
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as any;
  }
  
  const cloned: any = {};
  for (const key of Object.keys(obj as any)) {
    cloned[key] = deepClone((obj as any)[key]);
  }
  return cloned;
}
