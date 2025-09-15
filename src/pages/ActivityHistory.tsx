import React, { useEffect, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getRecentActivity, UsageHistoryItem } from '@/services/usage';
import { useAuth } from '@/contexts/AuthContext';
import { format } from 'date-fns';
import { marked } from 'marked';
import { Loader2 } from 'lucide-react';

const serviceTypeLabels: Record<string, string> = {
  contract_draft: 'Contract Drafting',
  compliance_check: 'Compliance Check'
};

const ActivityHistory = () => {
  const [activities, setActivities] = useState<UsageHistoryItem[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<UsageHistoryItem | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    async function loadActivity() {
      if (!user) return;
      
      try {
        const items = await getRecentActivity(user.id, 100); // Load more items for history
        setActivities(items);
        if (items.length > 0 && !selectedActivity) {
          setSelectedActivity(items[0]);
        }
      } catch (error) {
        console.error('Failed to load activity history:', error);
      } finally {
        setLoading(false);
      }
    }

    loadActivity();
  }, [user]);

  if (!user) {
    return null;
  }

  return (
    <div className="container mx-auto py-6 h-[calc(100vh-8rem)] flex flex-col">
      <div className="grid grid-cols-[300px_1fr] gap-6 flex-1 min-h-0">
        {/* Left panel */}
        <div className="border rounded-lg shadow-sm bg-background flex flex-col">
          <div className="p-4 border-b bg-muted/10">
            <h2 className="font-semibold">Activity History</h2>
          </div>
          <ScrollArea className="flex-1 min-h-0">
            <div className="space-y-1 p-2">
              {activities.map((activity) => (
                <button
                  key={activity.id}
                  onClick={() => setSelectedActivity(activity)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedActivity?.id === activity.id
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-accent'
                  }`}
                >
                  <div className="font-medium">
                    {serviceTypeLabels[activity.service_type] || activity.service_type}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {format(new Date(activity.created_at), 'MMM d, yyyy h:mm a')}
                  </div>
                  {activity.prompt_title && (
                    <div className="text-sm text-muted-foreground truncate mt-1">
                      {activity.prompt_title}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </ScrollArea>
        </div>
        
        <ScrollArea>{/* Right panel */}
        <div className="border rounded-lg shadow-sm bg-background flex flex-col">
            {loading ? (
            <div className="h-full flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : (
            <div className="flex flex-col h-full">
              <div className="border-b p-4 bg-muted/10 flex-shrink-0">
                <h2 className="font-semibold text-xl mb-2">
                  {serviceTypeLabels[selectedActivity?.service_type] || selectedActivity?.service_type}
                </h2>
                <div className="text-sm text-muted-foreground">
                  {selectedActivity ? format(new Date(selectedActivity.created_at), 'MMMM d, yyyy h:mm a') : ''}
                </div>
              </div>
                <div className="p-6">
                  {selectedActivity ? (
                    <div 
                      className="prose prose-sm dark:prose-invert max-w-none"
                      dangerouslySetInnerHTML={{
                        __html: marked(selectedActivity.prompt_output, { breaks: true })
                      }}
                    />
                  ) : (
                    <div className="flex items-center justify-center text-muted-foreground py-4">
                      Select an activity to view details
                    </div>
                  )}
                  </div>
                  
                </div>
              )}
        </div></ScrollArea>
      </div>
    </div>
  );
};

export default ActivityHistory;