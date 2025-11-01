/**
 * Ask Question Modal (Investors only)
 * Allows investors to ask questions about a startup
 */
import { useState } from 'react';
import { MessageSquarePlus } from 'lucide-react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useCreateQuestion } from '@/hooks/use-questions';
import type { QuestionCategory, QuestionPriority } from '@/types/questions';

interface AskQuestionModalProps {
  startupId: string;
  trigger?: React.ReactNode;
}

const categories: { value: QuestionCategory; label: string }[] = [
  { value: 'team', label: 'Team & Leadership' },
  { value: 'market', label: 'Market Opportunity' },
  { value: 'product', label: 'Product & Technology' },
  { value: 'financials', label: 'Financials & Metrics' },
  { value: 'business_model', label: 'Business Model' },
];

const priorities: { value: QuestionPriority; label: string }[] = [
  { value: 'low', label: 'Low Priority' },
  { value: 'medium', label: 'Medium Priority' },
  { value: 'high', label: 'High Priority' },
];

export function AskQuestionModal({ startupId, trigger }: AskQuestionModalProps) {
  const [open, setOpen] = useState(false);
  const [questionText, setQuestionText] = useState('');
  const [category, setCategory] = useState<QuestionCategory>('team');
  const [priority, setPriority] = useState<QuestionPriority>('medium');
  
  const createQuestion = useCreateQuestion();

  const handleSubmit = async () => {
    if (!questionText.trim()) return;

    createQuestion.mutate(
      {
        startup_id: startupId,
        question_text: questionText,
        category,
        priority,
        tags: [],
      },
      {
        onSuccess: () => {
          setOpen(false);
          setQuestionText('');
          setCategory('team');
          setPriority('medium');
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button size="lg" className="gap-2">
            <MessageSquarePlus className="h-5 w-5" />
            Ask a Question
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Ask a Question</DialogTitle>
          <DialogDescription>
            Ask the founder a question about their startup. They will be notified and can respond with details.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select value={category} onValueChange={(value) => setCategory(value as QuestionCategory)}>
              <SelectTrigger id="category">
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select value={priority} onValueChange={(value) => setPriority(value as QuestionPriority)}>
              <SelectTrigger id="priority">
                <SelectValue placeholder="Select priority" />
              </SelectTrigger>
              <SelectContent>
                {priorities.map((pri) => (
                  <SelectItem key={pri.value} value={pri.value}>
                    {pri.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="question">Your Question</Label>
            <Textarea
              id="question"
              placeholder="What would you like to know about this startup?"
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              rows={6}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              Be specific and clear. The founder will receive a notification.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!questionText.trim() || createQuestion.isPending}
          >
            {createQuestion.isPending ? 'Sending...' : 'Send Question'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
