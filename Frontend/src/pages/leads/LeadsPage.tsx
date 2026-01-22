import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { Button } from '../../components/common';
import { leadsApi } from '../../services/leads';
import { stagesApi } from '../../services/stages';
import { useAppSelector } from '../../hooks/useRedux';
import type { WorkItem } from '../../types';
import { LeadCard, CreateLeadModal } from '../../components/leads';

export const LeadsPage: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const selectedConfig = useAppSelector((state) => state.configs.selectedConfig);
  const queryClient = useQueryClient();

  const { data: leads } = useQuery({
    queryKey: ['leads', selectedConfig?.uid],
    queryFn: () => leadsApi.getAll(selectedConfig?.uid),
    enabled: !!selectedConfig,
  });

  const { data: stages } = useQuery({
    queryKey: ['stages', selectedConfig?.uid],
    queryFn: () => stagesApi.getAll(selectedConfig?.uid),
    enabled: !!selectedConfig,
  });

  const leadsArray = Array.isArray(leads) ? leads : [];
  const stagesArray = Array.isArray(stages) ? stages : [];

  const moveLeadMutation = useMutation({
    mutationFn: ({ leadUid, targetStage }: { leadUid: string; targetStage: string }) =>
      leadsApi.moveStage(leadUid, targetStage),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  const handleDragStart = (e: React.DragEvent, lead: WorkItem) => {
    e.dataTransfer.setData('leadUid', lead.uid);
  };

  const handleDrop = (e: React.DragEvent, targetStage: string) => {
    e.preventDefault();
    const leadUid = e.dataTransfer.getData('leadUid');
    if (leadUid) {
      moveLeadMutation.mutate({ leadUid, targetStage });
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  if (!selectedConfig) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Please select a workflow to view leads</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 mt-1">
            {leadsArray.length} leads in {selectedConfig.workflow_name}
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus size={20} className="mr-2" />
          New Lead
        </Button>
      </div>

      {stagesArray.length === 0 ? (
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-center">
            <p className="text-gray-500 text-lg mb-2">No stages found</p>
            <p className="text-gray-400 text-sm">Configure your workflow stages in settings</p>
          </div>
        </div>
      ) : (
        <>
          {/* Kanban Board */}
          <div className="flex space-x-4 overflow-x-auto pb-4">
            {stagesArray.map((stage) => {
              const stageLeads = leadsArray.filter((lead) => lead.current_stage === stage.uid || lead.stage === stage.uid);
          
          return (
            <div
              key={stage.uid}
              className="flex-shrink-0 w-80"
              onDrop={(e) => handleDrop(e, stage.uid)}
              onDragOver={handleDragOver}
            >
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: stage.color }}
                    />
                    <h3 className="font-semibold text-gray-900">{stage.name}</h3>
                    <span className="text-sm text-gray-500">({stageLeads.length})</span>
                  </div>
                </div>

                <div className="space-y-3">
                  {stageLeads.map((lead) => (
                    <LeadCard
                      key={lead.uid}
                      lead={lead}
                      onDragStart={handleDragStart}
                      onClick={() => {}}
                    />
                  ))}
                  
                  {stageLeads.length === 0 && (
                    <div className="text-center py-8 text-gray-400 text-sm">
                      No leads in this stage
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
        </>
      )}

      {/* Create Lead Modal */}
      <CreateLeadModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        configUid={selectedConfig.uid}
        stages={stagesArray}
      />
    </div>
  );
};
