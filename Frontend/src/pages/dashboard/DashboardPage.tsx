import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Layers, TrendingUp, DollarSign } from 'lucide-react';
import { Card } from '../../components/common';
import { leadsApi } from '../../services/leads';
import { stagesApi } from '../../services/stages';
import { useAppSelector } from '../../hooks/useRedux';

export const DashboardPage: React.FC = () => {
  const selectedConfig = useAppSelector((state) => state.configs.selectedConfig);

  const { data: leads, isLoading: leadsLoading } = useQuery({
    queryKey: ['leads', selectedConfig?.uid],
    queryFn: () => leadsApi.getAll(selectedConfig?.uid),
    enabled: !!selectedConfig,
  });

  const { data: stages, isLoading: stagesLoading } = useQuery({
    queryKey: ['stages', selectedConfig?.uid],
    queryFn: () => stagesApi.getAll(selectedConfig?.uid),
    enabled: !!selectedConfig,
  });

  // Convert to arrays with defaults
  const leadsArray = Array.isArray(leads) ? leads : [];
  const stagesArray = Array.isArray(stages) ? stages : [];

  // Show message if no config is selected
  if (!selectedConfig) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Workflow Selected</h2>
          <p className="text-gray-600">Please select a workflow from settings to get started.</p>
        </div>
      </div>
    );
  }

  // Show loading state
  if (leadsLoading || stagesLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Leads',
      value: leadsArray.length,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      title: 'Active Stages',
      value: stagesArray.filter((s) => s.is_active).length,
      icon: Layers,
      color: 'bg-green-500',
      change: '+5%',
    },
    {
      title: 'Conversion Rate',
      value: '24%',
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: '+3%',
    },
    {
      title: 'Total Value',
      value: '$125K',
      icon: DollarSign,
      color: 'bg-orange-500',
      change: '+18%',
    },
  ];

  const leadsByStage = stagesArray.map((stage) => ({
    stage,
    count: leadsArray.filter((lead) => lead.current_stage === stage.uid || lead.stage === stage.uid).length,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">
          {selectedConfig?.workflow_name || 'No workflow selected'}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className="p-0">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                    <p className="text-sm text-green-600 mt-2">{stat.change} from last month</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Leads by Stage */}
      <Card title="Leads by Stage" subtitle="Distribution across workflow stages">
        <div className="space-y-4">
          {leadsByStage.map(({ stage, count }) => (
            <div key={stage.uid} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: stage.color }}
                />
                <span className="font-medium text-gray-900">{stage.name}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-600">{count} leads</span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full"
                    style={{
                      backgroundColor: stage.color,
                      width: `${leadsArray.length > 0 ? (count / leadsArray.length) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Activity */}
      <Card title="Recent Activity" subtitle="Latest updates on leads">
        <div className="space-y-4">
          {leadsArray.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No leads yet. Create your first lead!</p>
          ) : (
            leadsArray.slice(0, 5).map((lead) => (
              <div key={lead.uid} className="flex items-center justify-between py-3 border-b last:border-0">
                <div>
                  <p className="font-medium text-gray-900">{lead.name}</p>
                  <p className="text-sm text-gray-500">{lead.email}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    (lead.properties?.priority || lead.priority) === 'high' ? 'bg-red-100 text-red-800' :
                    (lead.properties?.priority || lead.priority) === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {lead.properties?.priority || lead.priority || 'low'}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
};
