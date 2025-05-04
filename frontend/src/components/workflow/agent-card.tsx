// components/workflow/agent-card.tsx
'use client'

import { AgentPersona } from '@/types';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { UserCircle2 } from 'lucide-react';

interface AgentCardProps {
  persona: AgentPersona;
  workflowType: string;
}

export default function AgentCard({ persona, workflowType }: AgentCardProps) {
  // Format workflow type for display
  const formattedWorkflowType = workflowType
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
    
  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-100 to-blue-100 p-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-purple-500 flex items-center justify-center text-white">
            <UserCircle2 size={24} />
          </div>
          <div>
            <CardTitle className="text-lg">{persona.role}</CardTitle>
            <CardDescription>
              <Badge variant="outline" className="mt-1">
                {formattedWorkflowType}
              </Badge>
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-4">
        <p className="text-sm italic mb-3">&ldquo;{persona.persona}&rdquo;</p>
        <p className="text-sm mb-3">{persona.description}</p>
        
        <div className="mt-4">
          <h4 className="text-xs font-semibold uppercase tracking-wide mb-2 text-gray-500">
            Strengths
          </h4>
          <div className="flex flex-wrap gap-2">
            {(persona.strengths || []).map((strength, index) => (
              <Badge key={index} variant="secondary" className="bg-blue-50">
                {strength}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="bg-gray-50 px-4 py-3 text-xs text-gray-500">
        Agent ID: {persona.role ? persona.role.toLowerCase().replace(/\s+/g, '_') : 'unknown'}
      </CardFooter>
    </Card>
  );
}