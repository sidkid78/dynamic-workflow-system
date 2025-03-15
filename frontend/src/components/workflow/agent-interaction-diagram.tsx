// components/workflow/agent-interaction-diagram.tsx
import { useEffect, useRef } from 'react';
import { AgentResponse } from '@/types';
import * as d3 from 'd3';
import { truncate } from '@/lib/utils';

interface AgentInteractionDiagramProps {
  steps: AgentResponse[];
}

export default function AgentInteractionDiagram({ steps }: AgentInteractionDiagramProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current || !steps.length) return;
    
    // Clear previous diagram
    d3.select(svgRef.current).selectAll('*').remove();
    
    // Create diagram
    const svg = d3.select(svgRef.current);
    const width = 800;
    const height = 600;
    
    // Set up diagram container
    svg.attr('width', width)
       .attr('height', height)
       .attr('viewBox', `0 0 ${width} ${height}`)
       .attr('style', 'max-width: 100%; height: auto;');
    
    // Create a vertical timeline
    const timelineX = 100;
    const timelineStartY = 50;
    const timelineEndY = height - 50;
    
    // Draw timeline
    svg.append('line')
      .attr('x1', timelineX)
      .attr('y1', timelineStartY)
      .attr('x2', timelineX)
      .attr('y2', timelineEndY)
      .attr('stroke', '#aaa')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5');
    
    // Get unique agents
    const agents = Array.from(new Set(steps.map(step => step.agent_role)));
    
    // Assign colors to agents
    const colorScale = d3.scaleOrdinal<string>()
      .domain(agents)
      .range(d3.schemeCategory10);
    
    // Calculate position for each step
    const stepHeight = (timelineEndY - timelineStartY) / (steps.length + 1);
    
    // Draw agent nodes and messages
    steps.forEach((step, i) => {
      const y = timelineStartY + (i + 1) * stepHeight;
      
      // Draw step marker on timeline
      svg.append('circle')
        .attr('cx', timelineX)
        .attr('cy', y)
        .attr('r', 6)
        .attr('fill', '#fff')
        .attr('stroke', colorScale(step.agent_role))
        .attr('stroke-width', 2);
      
      // Draw agent node
      const agentX = 250;
      svg.append('circle')
        .attr('cx', agentX)
        .attr('cy', y)
        .attr('r', 20)
        .attr('fill', colorScale(step.agent_role))
        .attr('stroke', '#333')
        .attr('stroke-width', 1);
      
      // Add agent label
      svg.append('text')
        .attr('x', agentX)
        .attr('y', y - 30)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(step.agent_role);
      
      // Draw connection line
      svg.append('line')
        .attr('x1', timelineX)
        .attr('y1', y)
        .attr('x2', agentX - 20)
        .attr('y2', y)
        .attr('stroke', '#aaa')
        .attr('stroke-width', 1);
      
      // Draw message content
      const messageX = 350;
      const messageWidth = 350;
      const messageHeight = 80;
      
      // Message background
      svg.append('rect')
        .attr('x', messageX)
        .attr('y', y - messageHeight/2)
        .attr('width', messageWidth)
        .attr('height', messageHeight)
        .attr('rx', 5)
        .attr('ry', 5)
        .attr('fill', '#f5f5f5')
        .attr('stroke', colorScale(step.agent_role))
        .attr('stroke-width', 1);
      
      // Add message content
      svg.append('foreignObject')
        .attr('x', messageX + 10)
        .attr('y', y - messageHeight/2 + 10)
        .attr('width', messageWidth - 20)
        .attr('height', messageHeight - 20)
        .append('xhtml:div')
        .style('font-size', '12px')
        .style('overflow', 'hidden')
        .html(truncate(step.content, 200));
      
      // Draw connection from agent to message
      svg.append('line')
        .attr('x1', agentX + 20)
        .attr('y1', y)
        .attr('x2', messageX)
        .attr('y2', y)
        .attr('stroke', colorScale(step.agent_role))
        .attr('stroke-width', 1);
      
      // Add timestamp
      svg.append('text')
        .attr('x', timelineX - 10)
        .attr('y', y + 5)
        .attr('text-anchor', 'end')
        .attr('font-size', '10px')
        .attr('fill', '#666')
        .text(`Step ${i + 1}`);
    });
    
    // Add legend
    const legendX = width - 150;
    const legendY = 50;
    
    svg.append('text')
      .attr('x', legendX)
      .attr('y', legendY - 20)
      .attr('font-weight', 'bold')
      .attr('font-size', '14px')
      .text('Agents');
    
    agents.forEach((agent, i) => {
      const y = legendY + i * 25;
      
      // Legend color box
      svg.append('rect')
        .attr('x', legendX)
        .attr('y', y)
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', colorScale(agent));
      
      // Legend text
      svg.append('text')
        .attr('x', legendX + 25)
        .attr('y', y + 12)
        .attr('font-size', '12px')
        .text(agent);
    });
    
  }, [steps]);
  
  if (!steps.length) {
    return <div className="text-center py-8 text-gray-500">No processing steps available</div>;
  }
  
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 overflow-auto">
      <h3 className="text-lg font-medium mb-4">Agent Interaction Flow</h3>
      <div className="overflow-auto">
        <svg ref={svgRef} className="mx-auto" />
      </div>
    </div>
  );
}