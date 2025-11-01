import { useState, useRef } from 'react';
import { uploadStartupLogo } from '@/services/imageService';
import { Button } from '@/components/ui/button';
import { Upload, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Props {
  startupId: string;
  currentLogoUrl?: string;
  onUploadSuccess: (signedUrl: string, gcsPath: string) => void;
}

export function StartupLogoUpload({ startupId, currentLogoUrl, onUploadSuccess }: Props) {
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(currentLogoUrl);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => setPreviewUrl(reader.result as string);
    reader.readAsDataURL(file);

    setUploading(true);
    try {
      const result = await uploadStartupLogo(startupId, file);
      toast({ title: 'Success!', description: 'Logo uploaded' });
      onUploadSuccess(result.signed_url, result.gcs_path);
    } catch (error) {
      toast({ title: 'Failed', description: String(error), variant: 'destructive' });
      setPreviewUrl(currentLogoUrl);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex items-center gap-4">
      {previewUrl ? (
        <img src={previewUrl} alt="Logo" className="h-20 w-20 object-contain rounded-lg border" />
      ) : (
        <div className="h-20 w-20 border-2 border-dashed rounded-lg flex items-center justify-center">
          <Upload className="h-8 w-8 text-muted-foreground" />
        </div>
      )}
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/svg+xml"
          onChange={handleFileSelect}
          className="hidden"
        />
        <Button variant="outline" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
          <Upload className="h-4 w-4 mr-2" />
          {uploading ? 'Uploading...' : 'Upload Logo'}
        </Button>
        <p className="text-xs text-muted-foreground mt-2">JPG, PNG, WEBP or SVG. Max 5MB.</p>
      </div>
    </div>
  );
}
