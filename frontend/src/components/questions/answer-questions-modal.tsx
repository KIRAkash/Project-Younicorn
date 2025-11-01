/**
 * Answer Questions Modal (Founders only)
 * Allows founders to answer multiple questions at once with file attachments
 */
import { useState } from 'react';
import { MessageSquareReply, Paperclip, X, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import type { Question, AnswerAttachment } from '@/types/questions';
import { formatDistanceToNow } from 'date-fns';
import { storage } from '@/config/firebase';
import { ref, uploadBytes } from 'firebase/storage';

interface AnswerQuestionsModalProps {
  questions: Question[];
  startupId: string;
  trigger?: React.ReactNode;
}

interface QuestionAnswer {
  questionId: string;
  answerText: string;
  files: File[];
  attachments: AnswerAttachment[];
}

export function AnswerQuestionsModal({ questions, startupId, trigger }: AnswerQuestionsModalProps) {
  const [open, setOpen] = useState(false);
  const [answers, setAnswers] = useState<Record<string, QuestionAnswer>>({});
  const [uploading, setUploading] = useState(false);
  
  const { toast } = useToast();

  // Initialize answers state when modal opens
  const handleOpenChange = (isOpen: boolean) => {
    setOpen(isOpen);
    if (isOpen) {
      const initialAnswers: Record<string, QuestionAnswer> = {};
      questions.forEach((q) => {
        initialAnswers[q.id] = {
          questionId: q.id,
          answerText: '',
          files: [],
          attachments: [],
        };
      });
      setAnswers(initialAnswers);
    }
  };

  const handleAnswerChange = (questionId: string, text: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        answerText: text,
      },
    }));
  };

  const handleFileSelect = (questionId: string, files: FileList | null) => {
    if (!files) return;
    
    const fileArray = Array.from(files);
    setAnswers((prev) => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        files: [...prev[questionId].files, ...fileArray],
      },
    }));
  };

  const handleRemoveFile = (questionId: string, index: number) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        files: prev[questionId].files.filter((_, i) => i !== index),
      },
    }));
  };

  const uploadFile = async (file: File, questionId: string): Promise<AnswerAttachment> => {
    // Upload to GCS: startups/{startupId}/responses/{questionId}/{filename}
    const filePath = `startups/${startupId}/responses/${questionId}/${file.name}`;
    const storageRef = ref(storage, filePath);
    
    await uploadBytes(storageRef, file);
    
    return {
      filename: file.name,
      gcs_path: filePath,
      size: file.size,
      uploaded_at: new Date().toISOString(),
    };
  };

  const handleSubmitAll = async () => {
    setUploading(true);
    
    try {
      // Filter questions that have answers
      const questionsToAnswer = questions.filter(
        (q) => answers[q.id]?.answerText.trim()
      );

      if (questionsToAnswer.length === 0) {
        toast({
          title: 'No answers provided',
          description: 'Please provide at least one answer.',
          variant: 'destructive',
        });
        setUploading(false);
        return;
      }

      // Upload all files first and build bulk answer payload
      const bulkAnswerData: Array<{
        question_id: string;
        answer_text: string;
        attachments: AnswerAttachment[];
      }> = [];

      for (const question of questionsToAnswer) {
        const answer = answers[question.id];
        
        // Upload files if any
        const uploadedAttachments: AnswerAttachment[] = [];
        for (const file of answer.files) {
          try {
            const attachment = await uploadFile(file, question.id);
            uploadedAttachments.push(attachment);
          } catch (error) {
            console.error(`Failed to upload ${file.name}:`, error);
            toast({
              title: 'File upload failed',
              description: `Could not upload ${file.name}. Continuing with other files.`,
              variant: 'destructive',
            });
          }
        }

        bulkAnswerData.push({
          question_id: question.id,
          answer_text: answer.answerText,
          attachments: uploadedAttachments,
        });
      }

      // Submit all answers in a single bulk request
      const token = localStorage.getItem('token');
      const response = await fetch('/api/questions/bulk-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ answers: bulkAnswerData }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit answers');
      }

      const result = await response.json();

      // Handle response
      if (result.failed === 0) {
        toast({
          title: 'All answers submitted!',
          description: result.message,
        });

        // Show reanalysis notification if triggered
        if (result.reanalysis_triggered) {
          setTimeout(() => {
            toast({
              title: 'Reanalysis Triggered',
              description: 'All questions answered! A new analysis has been started automatically.',
            });
          }, 1000);
        }
      } else {
        // Partial success
        toast({
          title: 'Answers submitted',
          description: result.message,
          variant: 'default',
        });

        // Show which questions failed
        const failedResults = result.results.filter((r: any) => !r.success);
        if (failedResults.length > 0) {
          setTimeout(() => {
            toast({
              title: 'Some answers failed',
              description: `${failedResults.length} answer(s) could not be submitted.`,
              variant: 'destructive',
            });
          }, 500);
        }
      }

      setOpen(false);
      setAnswers({});
    } catch (error) {
      console.error('Error submitting answers:', error);
      toast({
        title: 'Submission failed',
        description: error instanceof Error ? error.message : 'Could not submit answers. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      team: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      market: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      product: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      financials: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      business_model: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {trigger || (
          <Button size="lg" className="gap-2">
            <MessageSquareReply className="h-5 w-5" />
            Add Responses
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[1200px] max-h-[120vh]">
        <DialogHeader>
          <DialogTitle>Answer Questions ({questions.length})</DialogTitle>
          <DialogDescription>
            Provide answers to investor questions. You can attach files to support your responses.
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="h-[500px] pr-4">
          <div className="space-y-6 py-4">
            {questions.map((question, index) => (
              <div key={question.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-muted-foreground">
                        Question {index + 1}
                      </span>
                      <Badge className={getCategoryColor(question.category)}>
                        {question.category.replace('_', ' ')}
                      </Badge>
                      {question.priority === 'high' && (
                        <Badge variant="destructive">High Priority</Badge>
                      )}
                    </div>
                    <p className="text-sm font-medium mb-1">{question.question_text}</p>
                    <p className="text-xs text-muted-foreground">
                      Asked by {question.asked_by_name} •{' '}
                      {formatDistanceToNow(new Date(question.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`answer-${question.id}`}>Your Answer</Label>
                  <Textarea
                    id={`answer-${question.id}`}
                    placeholder="Provide a detailed answer..."
                    value={answers[question.id]?.answerText || ''}
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    rows={4}
                    className="resize-none"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Attachments (optional)</Label>
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => document.getElementById(`file-${question.id}`)?.click()}
                      className="gap-2"
                    >
                      <Paperclip className="h-4 w-4" />
                      Attach Files
                    </Button>
                    <input
                      id={`file-${question.id}`}
                      type="file"
                      multiple
                      className="hidden"
                      onChange={(e) => handleFileSelect(question.id, e.target.files)}
                    />
                  </div>
                  
                  {answers[question.id]?.files.length > 0 && (
                    <div className="space-y-1">
                      {answers[question.id].files.map((file, fileIndex) => (
                        <div
                          key={fileIndex}
                          className="flex items-center justify-between p-2 bg-muted rounded text-sm"
                        >
                          <span className="truncate flex-1">{file.name}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => handleRemoveFile(question.id, fileIndex)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button onClick={handleSubmitAll} disabled={uploading}>
            {uploading ? (
              <>
                <Upload className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit All Answers'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
