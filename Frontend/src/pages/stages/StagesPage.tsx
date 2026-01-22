import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common';
import { stagesApi } from '../../services/stages';
import { useAppSelector } from '../../hooks/useRedux';

export const StagesPage: React.FC = () => {
  const selectedConfig = useAppSelector((state) => state.configs.selectedConfig);

  const { data: stages } = useQuery({
    queryKey: ['stages', selectedConfig?.uid],
    queryFn: () => stagesApi.getAll(selectedConfig?.uid),
    enabled: !!selectedConfig,
  });

  const stagesArray = Array.isArray(stages) ? stages : [];

  if (!selectedConfig) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Please select a workflow to view stages</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stages</h1>
          <p className="text-gray-500 mt-1">
            Manage workflow stages for {selectedConfig.workflow_name}
          </p>
        </div>
      </div>

      {stagesArray.length === 0 ? (
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-center">
            <p className="text-gray-500 text-lg mb-2">No stages configured</p>
            <p className="text-gray-400 text-sm">Add stages to your workflow in settings</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stagesArray.map((stage) => (
          <Card key={stage.uid} className="p-0">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: stage.color }}
                  />
                  <div>
                    <h3 className="font-semibold text-gray-900">{stage.name}</h3>
                    <p className="text-sm text-gray-500">Order: {stage.order}</p>
                  </div>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    stage.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {stage.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-4">{stage.description}</p>

              {stage.stage_tasks && stage.stage_tasks.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Tasks ({stage.stage_tasks.length})
                  </p>
                  <ul className="space-y-1">
                    {stage.stage_tasks.map((task) => (
                      <li key={task.uid} className="text-sm text-gray-600 flex items-center">
                        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2" />
                        {task.name}
                        {task.required && <span className="text-red-500 ml-1">*</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {stage.allowed_next_stages && stage.allowed_next_stages.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Can move to:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {stage.allowed_next_stages.map((nextStageUid) => {
                      const nextStage = stagesArray.find((s) => s.uid === nextStageUid);
                      return nextStage ? (
                        <span
                          key={nextStageUid}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {nextStage.name}
                        </span>
                      ) : null;
                    })}
                  </div>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>
      )}
    </div>
  );
};
