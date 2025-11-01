/**
 * Founder Dashboard
 * Shows founder's submitted startups and their analysis status
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Plus, Clock, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import axios from 'axios';

interface StartupSubmission {
  startup_id: string;
  company_name: string;
  industry: string;
  submission_date: string;
  analysis_status: 'pending' | 'in_progress' | 'completed' | 'failed';
  overall_score?: number;
}

export function FounderDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState<StartupSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const idToken = await user?.getIdToken();
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8080'}/api/founder/submissions`,
        {
          headers: {
            'Authorization': `Bearer ${idToken}`
          }
        }
      );
      setSubmissions(response.data.submissions || []);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load submissions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-blue-500 animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      completed: 'default',
      in_progress: 'secondary',
      failed: 'destructive',
      pending: 'outline'
    };
    return (
      <Badge variant={variants[status] || 'outline'}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const handleViewDetails = (startupId: string, status: string) => {
    if (status === 'completed') {
      navigate(`/founder/submission/${startupId}/analysis`);
    } else {
      navigate(`/founder/submission/${startupId}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Submissions</h1>
          <p className="text-muted-foreground mt-2">
            Track your startup submissions and analysis results
          </p>
        </div>
        <Button onClick={() => navigate('/submit')} size="lg">
          <Plus className="mr-2 h-4 w-4" />
          Submit New Startup
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Submissions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{submissions.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Analyses</CardTitle>
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {submissions.filter(s => s.analysis_status === 'completed').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {submissions.filter(s => s.analysis_status === 'in_progress').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="mb-8 border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Submissions List */}
      {submissions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">No submissions yet</h3>
              <p className="text-muted-foreground mb-6">
                Get started by submitting your startup for analysis
              </p>
              <Button onClick={() => navigate('/submit')}>
                <Plus className="mr-2 h-4 w-4" />
                Submit Your Startup
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {submissions.map((submission) => (
            <Card key={submission.startup_id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(submission.analysis_status)}
                      <CardTitle className="text-xl">{submission.company_name}</CardTitle>
                    </div>
                    <CardDescription className="flex items-center gap-4">
                      <span className="font-medium">{submission.industry}</span>
                      <span>•</span>
                      <span>Submitted {new Date(submission.submission_date).toLocaleDateString()}</span>
                    </CardDescription>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {getStatusBadge(submission.analysis_status)}
                    {submission.overall_score && (
                      <Badge variant="outline" className="text-lg font-bold">
                        Score: {submission.overall_score}/10
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center">
                  <div className="text-sm text-muted-foreground">
                    {submission.analysis_status === 'completed' && (
                      <span className="flex items-center gap-2 text-green-600">
                        <Sparkles className="h-4 w-4" />
                        Analysis complete! View your results
                      </span>
                    )}
                    {submission.analysis_status === 'in_progress' && (
                      <span className="flex items-center gap-2 text-blue-600">
                        <Clock className="h-4 w-4 animate-pulse" />
                        Analysis in progress...
                      </span>
                    )}
                    {submission.analysis_status === 'pending' && (
                      <span className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        Waiting to start analysis
                      </span>
                    )}
                    {submission.analysis_status === 'failed' && (
                      <span className="flex items-center gap-2 text-red-600">
                        <AlertCircle className="h-4 w-4" />
                        Analysis failed - please contact support
                      </span>
                    )}
                  </div>
                  <Button
                    onClick={() => handleViewDetails(submission.startup_id, submission.analysis_status)}
                    variant={submission.analysis_status === 'completed' ? 'default' : 'outline'}
                  >
                    {submission.analysis_status === 'completed' ? 'View Analysis' : 'View Details'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
