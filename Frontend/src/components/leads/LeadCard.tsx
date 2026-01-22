import React from 'react';
import { Mail, Phone, Calendar } from 'lucide-react';
import type { WorkItem } from '../../types';

interface LeadCardProps {
  lead: WorkItem;
  onDragStart: (e: React.DragEvent, lead: WorkItem) => void;
  onClick: () => void;
}

export const LeadCard: React.FC<LeadCardProps> = ({ lead, onDragStart, onClick }) => {
  const priorityColors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  };

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, lead)}
      onClick={onClick}
      className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-semibold text-gray-900">{lead.name}</h4>
        {lead.priority && (
          <span className={`px-2 py-1 rounded text-xs font-medium ${priorityColors[lead.priority]}`}>
            {lead.priority}
          </span>
        )}
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        {lead.email && (
          <div className="flex items-center space-x-2">
            <Mail size={14} />
            <span className="truncate">{lead.email}</span>
          </div>
        )}
        {lead.phone && (
          <div className="flex items-center space-x-2">
            <Phone size={14} />
            <span>{lead.phone}</span>
          </div>
        )}
        {lead.company && (
          <div className="text-sm font-medium text-gray-700 mt-2">
            {lead.company}
          </div>
        )}
      </div>

      {lead.tags && lead.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {lead.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {lead.created_at && (
        <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
          <Calendar size={12} />
          <span>{new Date(lead.created_at).toLocaleDateString()}</span>
        </div>
      )}
    </div>
  );
};
