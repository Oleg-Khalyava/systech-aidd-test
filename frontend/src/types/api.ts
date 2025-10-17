/**
 * TypeScript типы для Backend API
 * На основе контракта из api/models.py
 */

export interface KPIMetric {
    label: string;
    value: string;
    change: number;
    trend: 'up' | 'down' | 'stable';
}

export interface TimelinePoint {
    date: string; // ISO format: "2025-10-17"
    value: number;
}

export interface StatsResponse {
    kpi_metrics: KPIMetric[];
    timeline: TimelinePoint[];
}

export type Period = 'day' | 'week' | 'month';

