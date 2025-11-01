import { auth } from '@/config/firebase';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export interface ImageUploadResponse {
  gcs_path: string;
  signed_url: string;
  message: string;
}

/**
 * Upload profile icon for current user
 * Max size: 2MB, Formats: jpg, png, webp
 */
export async function uploadProfileIcon(file: File): Promise<ImageUploadResponse> {
  if (file.size > 2 * 1024 * 1024) {
    throw new Error('Profile icon must be less than 2MB');
  }

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Only JPG, PNG, and WEBP formats are allowed');
  }

  const user = auth.currentUser;
  if (!user) throw new Error('Not logged in');
  const token = await user.getIdToken();

  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_URL}/api/images/upload/profile-icon`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Upload failed');
  }
  return res.json();
}

/**
 * Upload startup logo
 * Max size: 5MB, Formats: jpg, png, webp, svg
 */
export async function uploadStartupLogo(startupId: string, file: File): Promise<ImageUploadResponse> {
  if (file.size > 5 * 1024 * 1024) {
    throw new Error('Max 5MB');
  }

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/svg+xml'];
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Only JPG, PNG, WEBP, and SVG are allowed');
  }

  const user = auth.currentUser;
  if (!user) throw new Error('Not logged in');
  const token = await user.getIdToken();

  const formData = new FormData();
  formData.append('startup_id', startupId);
  formData.append('file', file);

  const res = await fetch(`${API_URL}/api/images/upload/startup-logo`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Upload failed');
  }
  return res.json();
}
