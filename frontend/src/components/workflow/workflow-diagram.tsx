// components/workflow/workflow-diagram.tsx
import { useEffect, useRef } from 'react';
import { WorkflowSelection } from '@/types';
import * as d3 from 'd3';
import { titleCase } from '@/lib/utils';

interface WorkflowDiagramProps {
  workflowInfo: WorkflowSelection;
  intermediateSteps: {
    agent_role: string;
    content: string;
  }[];
}

export default function WorkflowDiagram({ workflowInfo, intermediateSteps }: WorkflowDiagramProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current || !workflowInfo) return;
    
    // Clear previous diagram
    d3.select(svgRef.current).selectAll('*').remove();
    
    // Create diagram based on workflow type
    const workflowType = workflowInfo.selected_workflow;
    const svg = d3.select(svgRef.current);
    const width = 700;
    const height = 400;
    
    // Set up diagram container
    svg.attr('width', width)
       .attr('height', height)
       .attr('viewBox', `0 0 ${width} ${height}`)
       .attr('style', 'max-width: 100%; height: auto;');
       
    // Add arrow marker
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#333');
    
    // Find if a step has been completed by a specific agent role
    const isStepCompleted = (role: string): boolean => {
      return intermediateSteps.some(step => 
        step.agent_role.toLowerCase().includes(role.toLowerCase()));
    };
    
    // Different diagram layouts based on workflow type
    switch (workflowType) {
      case 'prompt_chaining':
        renderPromptChainingDiagram(svg, isStepCompleted);
        break;
      case 'routing':
        renderRoutingDiagram(svg, isStepCompleted);
        break;
      case 'parallel_sectioning':
        renderParallelSectioningDiagram(svg, isStepCompleted);
        break;
      case 'parallel_voting':
        renderParallelVotingDiagram(svg, isStepCompleted);
        break;
      case 'orchestrator_workers':
        renderOrchestratorWorkersDiagram(svg, isStepCompleted);
        break;
      case 'evaluator_optimizer':
        renderEvaluatorOptimizerDiagram(svg, isStepCompleted);
        break;
      default:
        renderDefaultDiagram(svg, workflowType);
    }
  }, [workflowInfo, intermediateSteps]);
  
  // Formatting helper for the workflow name display
  const formattedWorkflowName = workflowInfo && workflowInfo.selected_workflow ? 
    titleCase(workflowInfo.selected_workflow.replace(/_/g, ' ')) : 
    'Unknown Workflow';
  
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="p-4 border-b">
        <h3 className="text-lg font-medium">
          {formattedWorkflowName} Workflow
        </h3>
        <p className="text-sm text-gray-600 mt-1">{workflowInfo?.reasoning}</p>
      </div>
      <div className="p-4 overflow-auto">
        <svg ref={svgRef} className="mx-auto" />
      </div>
    </div>
  );
}

// Render Prompt Chaining Workflow
function renderPromptChainingDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, isStepCompleted: (role: string) => boolean) {
  const nodes = [
    { id: 'user', label: 'User', x: 100, y: 50, completed: true },
    { id: 'step1', label: 'Initial Processor', x: 300, y: 50, completed: isStepCompleted('Initial Processor') },
    { id: 'gate', label: 'Validator', x: 300, y: 150, completed: isStepCompleted('Validator') },
    { id: 'step2', label: 'Refiner', x: 300, y: 250, completed: isStepCompleted('Refiner') },
    { id: 'response', label: 'Final Response', x: 100, y: 250, completed: true }
  ];
  
  const links = [
    { source: 'user', target: 'step1' },
    { source: 'step1', target: 'gate' },
    { source: 'gate', target: 'step2' },
    { source: 'step2', target: 'response' }
  ];
  
  renderNodes(svg, nodes);
  renderLinks(svg, links, nodes);
}

// Render Routing Workflow
function renderRoutingDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, isStepCompleted: (role: string) => boolean) {
  const nodes = [
    { id: 'user', label: 'User', x: 350, y: 50, completed: true },
    { id: 'classifier', label: 'Query Classifier', x: 350, y: 150, completed: isStepCompleted('Classifier') },
    { id: 'cat1', label: 'Specialist 1', x: 150, y: 250, completed: isStepCompleted('Specialist') || isStepCompleted('support') },
    { id: 'cat2', label: 'Specialist 2', x: 350, y: 250, completed: isStepCompleted('Specialist') || isStepCompleted('management') },
    { id: 'cat3', label: 'Specialist 3', x: 550, y: 250, completed: isStepCompleted('Specialist') || isStepCompleted('inquiry') },
    { id: 'response', label: 'Final Response', x: 350, y: 350, completed: true }
  ];
  
  const links = [
    { source: 'user', target: 'classifier' },
    { source: 'classifier', target: 'cat1' },
    { source: 'classifier', target: 'cat2' },
    { source: 'classifier', target: 'cat3' },
    { source: 'cat1', target: 'response' },
    { source: 'cat2', target: 'response' },
    { source: 'cat3', target: 'response' }
  ];
  
  renderNodes(svg, nodes);
  renderLinks(svg, links, nodes);
}

// Render Parallel Sectioning Workflow
function renderParallelSectioningDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, isStepCompleted: (role: string) => boolean) {
  const nodes = [
    { id: 'user', label: 'User', x: 350, y: 50, completed: true },
    { id: 'sectioning', label: 'Task Divider', x: 350, y: 125, completed: isStepCompleted('Divider') || isStepCompleted('Task Divider') },
    { id: 'worker1', label: 'Section Worker 1', x: 150, y: 200, completed: isStepCompleted('Specialist') || isStepCompleted('Perspective') },
    { id: 'worker2', label: 'Section Worker 2', x: 350, y: 200, completed: isStepCompleted('Specialist') || isStepCompleted('Perspective') },
    { id: 'worker3', label: 'Section Worker 3', x: 550, y: 200, completed: isStepCompleted('Specialist') || isStepCompleted('Perspective') },
    { id: 'aggregator', label: 'Results Integrator', x: 350, y: 275, completed: isStepCompleted('Integrator') || isStepCompleted('Results Integrator') },
    { id: 'response', label: 'Final Response', x: 350, y: 350, completed: true }
  ];
  
  const links = [
    { source: 'user', target: 'sectioning' },
    { source: 'sectioning', target: 'worker1' },
    { source: 'sectioning', target: 'worker2' },
    { source: 'sectioning', target: 'worker3' },
    { source: 'worker1', target: 'aggregator' },
    { source: 'worker2', target: 'aggregator' },
    { source: 'worker3', target: 'aggregator' },
    { source: 'aggregator', target: 'response' }
  ];
  
  renderNodes(svg, nodes);
  renderLinks(svg, links, nodes);
}

// Render Parallel Voting Workflow
function renderParallelVotingDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, isStepCompleted: (role: string) => boolean) {
  const nodes = [
    { id: 'user', label: 'User', x: 350, y: 50, completed: true },
    { id: 'coordinator', label: 'Perspective Coordinator', x: 350, y: 125, completed: isStepCompleted('Coordinator') },
    { id: 'voter1', label: 'Perspective 1', x: 125, y: 200, completed: isStepCompleted('Evaluator') || isStepCompleted('Perspective') },
    { id: 'voter2', label: 'Perspective 2', x: 350, y: 200, completed: isStepCompleted('Evaluator') || isStepCompleted('Perspective') },
    { id: 'voter3', label: 'Perspective 3', x: 575, y: 200, completed: isStepCompleted('Evaluator') || isStepCompleted('Perspective') },
    { id: 'consensus', label: 'Consensus Builder', x: 350, y: 275, completed: isStepCompleted('Consensus') || isStepCompleted('Builder') },
    { id: 'response', label: 'Final Response', x: 350, y: 350, completed: true }
  ];
  
  const links = [
    { source: 'user', target: 'coordinator' },
    { source: 'coordinator', target: 'voter1' },
    { source: 'coordinator', target: 'voter2' },
    { source: 'coordinator', target: 'voter3' },
    { source: 'voter1', target: 'consensus' },
    { source: 'voter2', target: 'consensus' },
    { source: 'voter3', target: 'consensus' },
    { source: 'consensus', target: 'response' }
  ];
  
  renderNodes(svg, nodes);
  renderLinks(svg, links, nodes);
}

// Render Orchestrator-Workers Workflow
function renderOrchestratorWorkersDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, isStepCompleted: (role: string) => boolean) {
  const nodes = [
    { id: 'user', label: 'User', x: 350, y: 30, completed: true },
    { id: 'orchestrator', label: 'Task Coordinator', x: 350, y: 100, completed: isStepCompleted('Coordinator') || isStepCompleted('Orchestrator') },
    { id: 'worker1', label: 'Worker 1', x: 160, y: 170, completed: isStepCompleted('Specialist') || isStepCompleted('Worker') },
    { id: 'worker2', label: 'Worker 2', x: 350, y: 170, completed: isStepCompleted('Specialist') || isStepCompleted('Worker') },
    { id: 'worker3', label: 'Worker 3', x: 540, y: 170, completed: isStepCompleted('Specialist') || isStepCompleted('Worker') },
    { id: 'worker4', label: 'Worker 4', x: 160, y: 240, completed: isStepCompleted('Specialist') || isStepCompleted('Worker') },
    { id: 'worker5', label: 'Worker 5', x: 350, y: 240, completed: isStepCompleted('Specialist') || isStepCompleted('Worker') },
    { id: 'worker6', label: 'Worker 6', x: 540, y: 240, completed: isStepCompleted('Specialist') || isStepCompleted('Worker') },
    { id: 'synthesizer', label: 'Results Integrator', x: 350, y: 310, completed: isStepCompleted('Integrator') || isStepCompleted('Synthesizer') },
    { id: 'response', label: 'Final Response', x: 350, y: 380, completed: true }
  ];
  
  const links = [
    { source: 'user', target: 'orchestrator' },
    { source: 'orchestrator', target: 'worker1' },
    { source: 'orchestrator', target: 'worker2' },
    { source: 'orchestrator', target: 'worker3' },
    { source: 'orchestrator', target: 'worker4' },
    { source: 'orchestrator', target: 'worker5' },
    { source: 'orchestrator', target: 'worker6' },
    { source: 'worker1', target: 'synthesizer' },
    { source: 'worker2', target: 'synthesizer' },
    { source: 'worker3', target: 'synthesizer' },
    { source: 'worker4', target: 'synthesizer' },
    { source: 'worker5', target: 'synthesizer' },
    { source: 'worker6', target: 'synthesizer' },
    { source: 'synthesizer', target: 'response' }
  ];
  
  renderNodes(svg, nodes);
  renderLinks(svg, links, nodes);
}

// Render Evaluator-Optimizer Workflow
function renderEvaluatorOptimizerDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, isStepCompleted: (role: string) => boolean) {
  const nodes = [
    { id: 'user', label: 'User', x: 100, y: 50, completed: true },
    { id: 'criteria', label: 'Criteria Designer', x: 300, y: 50, completed: isStepCompleted('Designer') || isStepCompleted('Criteria') },
    { id: 'generator', label: 'Content Creator', x: 300, y: 150, completed: isStepCompleted('Creator') || isStepCompleted('Generator') },
    { id: 'evaluator', label: 'Quality Assessor', x: 450, y: 200, completed: isStepCompleted('Assessor') || isStepCompleted('Evaluator') },
    { id: 'optimizer', label: 'Refinement Specialist', x: 300, y: 250, completed: isStepCompleted('Specialist') || isStepCompleted('Optimizer') },
    { id: 'response', label: 'Final Response', x: 100, y: 250, completed: true }
  ];
  
  const links = [
    { source: 'user', target: 'criteria' },
    { source: 'criteria', target: 'generator' },
    { source: 'generator', target: 'evaluator' },
    { source: 'evaluator', target: 'optimizer' },
    { source: 'optimizer', target: 'response' },
    // Feedback loop
    { source: 'optimizer', target: 'evaluator', curved: true }
  ];
  
  renderNodes(svg, nodes);
  renderLinks(svg, links, nodes);
  
  // Add feedback loop label
  svg.append('text')
     .attr('x', 410)
     .attr('y', 225)
     .attr('text-anchor', 'middle')
     .attr('font-size', '10px')
     .attr('fill', '#666')
     .text('Feedback Loop');
}

// Default diagram for unknown workflow types
function renderDefaultDiagram(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, workflowType: string) {
  svg.append('text')
     .attr('x', 350)
     .attr('y', 200)
     .attr('text-anchor', 'middle')
     .attr('font-size', '16px')
     .attr('fill', '#666')
     .text(`No diagram available for ${workflowType}`);
}

// Helper function to render nodes
function renderNodes(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, nodes: any[]) {
  const nodeGroup = svg.append('g').attr('class', 'nodes');
  
  // Draw node circles
  nodeGroup.selectAll('circle')
    .data(nodes)
    .enter()
    .append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', 30)
    .attr('fill', d => d.completed ? '#4CAF50' : '#9E9E9E')
    .attr('stroke', '#333')
    .attr('stroke-width', 2);
  
  // Draw node labels
  nodeGroup.selectAll('text')
    .data(nodes)
    .enter()
    .append('text')
    .attr('x', d => d.x)
    .attr('y', d => d.y + 45)
    .attr('text-anchor', 'middle')
    .attr('font-family', 'Arial')
    .attr('font-size', 12)
    .text(d => d.label);
}

// Helper function to render links
function renderLinks(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, links: any[], nodes: any[]) {
  const linkGroup = svg.append('g').attr('class', 'links');
  
  // Function to find node by ID
  const findNode = (id: string) => nodes.find(n => n.id === id);
  
  // Draw links
  links.forEach(link => {
    const source = findNode(link.source);
    const target = findNode(link.target);
    
    if (source && target) {
      // For curved links (used in feedback loops)
      if (link.curved) {
        // Calculate control point for curved path
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const normalX = -dy;
        const normalY = dx;
        const length = Math.sqrt(normalX * normalX + normalY * normalY);
        const normalizedX = normalX / length * 50; // Control the curve strength
        const normalizedY = normalY / length * 50;
        
        linkGroup.append('path')
          .attr('d', `M${source.x},${source.y} Q${midX + normalizedX},${midY + normalizedY} ${target.x},${target.y}`)
          .attr('fill', 'none')
          .attr('stroke', '#333')
          .attr('stroke-width', 2)
          .attr('marker-end', 'url(#arrow)');
      } else {
        // Straight links
        linkGroup.append('line')
          .attr('x1', source.x)
          .attr('y1', source.y)
          .attr('x2', target.x)
          .attr('y2', target.y)
          .attr('stroke', '#333')
          .attr('stroke-width', 2)
          .attr('marker-end', 'url(#arrow)');
      }
    }
  });
}