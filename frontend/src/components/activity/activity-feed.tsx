/**
 * Activity Feed Component
 * Displays recent activity for a startup
 */
import { Activity as ActivityIcon, MessageSquare, MessageSquareReply, TrendingUp } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useStartupActivity } from '@/hooks/use-activity';
import type { Activity as ActivityType } from '@/types/questions';

interface ActivityFeedProps {
  startupId: string;
  limit?: number;
}

export function ActivityFeed({ startupId, limit = 20 }: ActivityFeedProps) {
  const { data: activities = [], isLoading } = useStartupActivity(startupId, limit);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'question_asked':
        return <MessageSquare className="h-4 w-4 text-blue-600" />;
      case 'answer_provided':
        return <MessageSquareReply className="h-4 w-4 text-green-600" />;
      case 'analysis_complete':
        return <TrendingUp className="h-4 w-4 text-purple-600" />;
      default:
        return <ActivityIcon className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'question_asked':
        return 'border-l-blue-600';
      case 'answer_provided':
        return 'border-l-green-600';
      case 'analysis_complete':
        return 'border-l-purple-600';
      default:
        return 'border-l-gray-600';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ActivityIcon className="h-5 w-5" />
            Activity Feed
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Loading activity...
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ActivityIcon className="h-5 w-5" />
          Activity Feed
        </CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <div className="text-center py-8">
            <ActivityIcon className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
            <p className="text-muted-foreground">No activity yet</p>
          </div>
        ) : (
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-4">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className={`flex gap-3 pb-4 border-l-2 pl-4 ${getActivityColor(activity.activity_type)}`}
                >
                  <div className="mt-1">{getActivityIcon(activity.activity_type)}</div>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium">{activity.description}</p>
                    <p className="text-xs text-muted-foreground">
                      {activity.user_name} •{' '}
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                    </p>
                    {activity.metadata && (
                      <div className="text-xs text-muted-foreground">
                        {activity.metadata.category && (
                          <span className="capitalize">
                            Category: {activity.metadata.category.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
