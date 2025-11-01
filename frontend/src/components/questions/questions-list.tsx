/**
 * Questions List Component
 * Displays questions with answers in a clean format
 */
import { MessageSquare, CheckCircle2, Clock, Paperclip, Sparkles } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import type { Question } from '@/types/questions';
import { cn } from '@/utils';

interface QuestionsListProps {
  questions: Question[];
  emptyMessage?: string;
}

export function QuestionsList({ questions, emptyMessage = 'No questions yet' }: QuestionsListProps) {
  if (questions.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      team: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 border border-blue-200 dark:border-blue-800',
      market: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 border border-green-200 dark:border-green-800',
      product: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300 border border-purple-200 dark:border-purple-800',
      financials: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
      business_model: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300 border border-pink-200 dark:border-pink-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border border-gray-200';
  };

  return (
    <div className="space-y-4">
      {questions.map((question) => (
        <Card key={question.id} className="border-none shadow-md hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-0">
            {/* Question Header with Gradient Background */}
            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 p-4 rounded-t-xl">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <Badge className={getCategoryColor(question.category)}>
                    {question.category.replace('_', ' ')}
                  </Badge>
                  {question.priority === 'high' && (
                    <Badge variant="destructive" className="text-xs">High Priority</Badge>
                  )}
                  {question.status === 'answered' ? (
                    <Badge variant="outline" className="gap-1 bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800">
                      <CheckCircle2 className="h-3 w-3" />
                      Answered
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="gap-1 bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950 dark:text-orange-300 dark:border-orange-800">
                      <Clock className="h-3 w-3" />
                      Pending
                    </Badge>
                  )}
                  {question.is_ai_generated && (
                    <Badge variant="outline" className="gap-1 bg-gradient-to-r from-blue-50 to-cyan-50 text-blue-700 border-blue-200 dark:from-blue-900/50 dark:to-cyan-900/50 dark:text-cyan-300 dark:border-cyan-700">
                      <Sparkles className="h-3 w-3" />
                      Added by Younicorn
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Asked by <span className="font-medium">{question.asked_by_name}</span> •{' '}
                  {formatDistanceToNow(new Date(question.created_at), { addSuffix: true })}
                </p>
              </div>
            </div>

            {/* Question Text */}
            <div className="bg-white dark:bg-gray-900 p-4 rounded-lg border-2 border-blue-200 dark:border-blue-700">
              <p className="text-base font-medium text-gray-900 dark:text-gray-100">{question.question_text}</p>
            </div>
            </div>

            {/* Answer Section */}
            {question.answer && (
              <div className="p-4 bg-gradient-to-r from-green-50/50 to-emerald-50/50 dark:from-green-950/20 dark:to-emerald-950/20">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-green-700 dark:text-green-400">
                    <CheckCircle2 className="h-4 w-4" />
                    <span>
                      Answered by <span className="font-semibold">{question.answer.answered_by_name}</span> •{' '}
                      {question.answer.answered_at &&
                        formatDistanceToNow(new Date(question.answer.answered_at), { addSuffix: true })}
                    </span>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-900 p-4 rounded-lg border-2 border-green-200 dark:border-green-800">
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{question.answer.answer_text}</p>
                    
                    {question.answer.attachments && question.answer.attachments.length > 0 && (
                      <div className="space-y-2 mt-4 pt-4 border-t border-green-200 dark:border-green-800">
                        <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-1">
                          <Paperclip className="h-3 w-3" />
                          Attachments ({question.answer.attachments.length})
                        </p>
                        <div className="space-y-2">
                          {question.answer.attachments.map((attachment, index) => (
                            <div
                              key={index}
                              className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-950/30 rounded-lg border border-green-200 dark:border-green-800 text-xs"
                            >
                              <Paperclip className="h-3 w-3 text-green-600 dark:text-green-400" />
                              <span className="flex-1 truncate font-medium text-gray-700 dark:text-gray-300">{attachment.filename}</span>
                              <span className="text-gray-600 dark:text-gray-400">
                                {(attachment.size / 1024).toFixed(1)} KB
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
