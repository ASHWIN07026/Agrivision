// Remove only retired SDK session keys; keep language settings and other app data.
export function clearRetiredAccountSession(storage) {
  try {
    const keys = [];
    for (let index = 0; index < storage.length; index++) {
      const key = storage.key(index);
      if (/^sb-[a-z0-9]+-auth-token(?:-(?:code-verifier|user))?$/.test(key || '')) keys.push(key);
    }
    for (const key of keys) storage.removeItem(key);
  } catch { /* Browser storage restrictions must not prevent public tools loading. */ }
}
