package com.agrivision.app;
import android.content.*;
import android.database.*;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.*;

public class PhotoProvider extends ContentProvider {
    private File photo(Uri uri) throws FileNotFoundException {
        if (!"com.agrivision.app.photos".equals(uri.getAuthority()) || !"/leaf-camera.jpg".equals(uri.getPath())) throw new FileNotFoundException("Unknown photo");
        return new File(getContext().getCacheDir(), "leaf-camera.jpg");
    }
    @Override public boolean onCreate() { return true; }
    @Override public String getType(Uri uri) { return "image/jpeg"; }
    @Override public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        File file = photo(uri);
        int flags;
        if ("r".equals(mode)) flags = ParcelFileDescriptor.MODE_READ_ONLY;
        else if ("w".equals(mode) || "wt".equals(mode)) flags = ParcelFileDescriptor.MODE_WRITE_ONLY | ParcelFileDescriptor.MODE_CREATE | ParcelFileDescriptor.MODE_TRUNCATE;
        else if ("rw".equals(mode)) flags = ParcelFileDescriptor.MODE_READ_WRITE | ParcelFileDescriptor.MODE_CREATE;
        else throw new FileNotFoundException("Unsupported mode");
        return ParcelFileDescriptor.open(file, flags);
    }
    @Override public Cursor query(Uri uri, String[] projection, String selection, String[] args, String sort) {
        try { File file = photo(uri); String[] cols = projection == null ? new String[]{OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE} : projection;
            MatrixCursor cursor = new MatrixCursor(cols); Object[] values = new Object[cols.length];
            for (int i = 0; i < cols.length; i++) values[i] = OpenableColumns.DISPLAY_NAME.equals(cols[i]) ? file.getName() : OpenableColumns.SIZE.equals(cols[i]) ? file.length() : null;
            cursor.addRow(values); return cursor;
        } catch (FileNotFoundException ignored) { return null; }
    }
    @Override public Uri insert(Uri uri, ContentValues values) { throw new UnsupportedOperationException(); }
    @Override public int delete(Uri uri, String selection, String[] args) { throw new UnsupportedOperationException(); }
    @Override public int update(Uri uri, ContentValues values, String selection, String[] args) { throw new UnsupportedOperationException(); }
}
