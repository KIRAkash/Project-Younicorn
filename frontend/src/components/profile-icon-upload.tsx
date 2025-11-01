import { useState, useRef } from 'react';
import { uploadProfileIcon } from '@/services/imageService';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Camera, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Props {
  currentIconUrl?: string;
  userName: string;
  onUploadSuccess: (signedUrl: string, gcsPath: string) => void;
}

export function ProfileIconUpload({ currentIconUrl, userName, onUploadSuccess }: Props) {
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(currentIconUrl);
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
      const result = await uploadProfileIcon(file);
      toast({ title: 'Success!', description: 'Profile icon uploaded' });
      onUploadSuccess(result.signed_url, result.gcs_path);
    } catch (error) {
      toast({ title: 'Failed', description: String(error), variant: 'destructive' });
      setPreviewUrl(currentIconUrl);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <Avatar className="h-24 w-24">
          <AvatarImage src={previewUrl} alt={userName} />
          <AvatarFallback>{userName[0]}</AvatarFallback>
        </Avatar>
        {uploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full">
            <Loader2 className="h-8 w-8 animate-spin text-white" />
          </div>
        )}
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileSelect}
        className="hidden"
      />
      <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
        <Camera className="h-4 w-4 mr-2" />
        {uploading ? 'Uploading...' : 'Change Photo'}
      </Button>
      <p className="text-xs text-muted-foreground">JPG, PNG or WEBP. Max 2MB.</p>
    </div>
  );
}
