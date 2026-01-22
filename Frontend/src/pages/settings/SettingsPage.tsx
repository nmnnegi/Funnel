import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common';
import { configsApi } from '../../services/configs';
import { useAppDispatch, useAppSelector } from '../../hooks/useRedux';
import { setSelectedConfig } from '../../store/slices/configsSlice';
import { Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const selectedConfig = useAppSelector((state) => state.configs.selectedConfig);

  const { data: configs } = useQuery({
    queryKey: ['configs'],
    queryFn: configsApi.getAll,
  });

  const configsArray = Array.isArray(configs) ? configs : [];

  const handleSelectConfig = (config: any) => {
    dispatch(setSelectedConfig(config));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your workflows and preferences</p>
      </div>

      <Card title="Workflows" subtitle="Select and manage your lead workflows">
        {configsArray.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-2">No workflows configured</p>
            <p className="text-gray-400 text-sm">Create your first workflow to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {configsArray.map((config) => (
            <div
              key={config.uid}
              onClick={() => handleSelectConfig(config)}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedConfig?.uid === config.uid
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="font-semibold text-gray-900">{config.workflow_name}</h3>
                    {selectedConfig?.uid === config.uid && (
                      <Check size={20} className="text-primary-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">UID: {config.uid}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        config.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {config.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {config.variables && (
                      <span className="text-sm text-gray-600">
                        {config.variables.length} custom fields
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {config.variables && config.variables.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">Custom Fields:</p>
                  <div className="flex flex-wrap gap-2">
                    {config.variables.map((field) => (
                      <span
                        key={field.field_key}
                        className="px-2 py-1 bg-white border border-gray-200 rounded text-xs"
                      >
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
        )}
      </Card>

      <Card title="Application Settings" subtitle="Configure your application preferences">
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">Email Notifications</p>
              <p className="text-sm text-gray-500">Receive email updates for new leads</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">Dark Mode</p>
              <p className="text-sm text-gray-500">Switch to dark theme</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </Card>
    </div>
  );
};
