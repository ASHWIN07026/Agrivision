import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareCameraPhoto } from '../src/utils/cameraPhoto.js';

test('camera photo keeps small files and resizes large captures, releasing previews', async () => {
  const saved = { Image: globalThis.Image, document: globalThis.document, create: URL.createObjectURL, revoke: URL.revokeObjectURL };
  let width = 800, height = 600, released = 0, canvas;
  URL.createObjectURL = () => 'blob:photo';
  URL.revokeObjectURL = () => { released++; };
  globalThis.Image = class { async decode() { this.naturalWidth = width; this.naturalHeight = height; } };
  globalThis.document = { createElement: () => (canvas = { getContext: () => ({ drawImage() {} }), toBlob: (fn) => fn(new Blob(['photo'], { type: 'image/jpeg' })) }) };
  try {
    const small = new File(['small'], 'small.jpg', { type: 'image/jpeg' });
    assert.equal(await prepareCameraPhoto(small), small);
    width = 6000; height = 4000;
    const result = await prepareCameraPhoto(small);
    assert.equal(canvas.width, 1600);
    assert.equal(canvas.height, 1067);
    assert.equal(result.type, 'image/jpeg');
    assert.equal(released, 2);
    globalThis.Image = class { async decode() { throw new Error('decode failed'); } };
    await assert.rejects(prepareCameraPhoto(small), /decode failed/);
    assert.equal(released, 3);
  } finally {
    globalThis.Image = saved.Image; globalThis.document = saved.document;
    URL.createObjectURL = saved.create; URL.revokeObjectURL = saved.revoke;
  }
});

test('camera rejects unsupported formats and oversized originals', async () => {
  await assert.rejects(prepareCameraPhoto({ type: 'image/heic', size: 100 }), /JPG or PNG/);
  await assert.rejects(prepareCameraPhoto({ type: 'image/jpeg', size: 31 * 1024 * 1024 }), /too large/);
});
