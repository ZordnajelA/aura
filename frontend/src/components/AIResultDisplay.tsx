import { useState } from 'react'
import {
  Brain,
  CheckCircle2,
  Circle,
  AlertCircle,
  Lightbulb,
  Tag,
  FolderOpen,
  Briefcase
} from 'lucide-react'
import type { TextClassification, ProcessedContent } from '../types'

interface AIResultDisplayProps {
  classification?: TextClassification | null
  processedContent?: ProcessedContent | null
  compact?: boolean
}

export default function AIResultDisplay({
  classification,
  processedContent,
  compact = false
}: AIResultDisplayProps) {
  const [checkedTasks, setCheckedTasks] = useState<Set<number>>(new Set())

  const toggleTask = (index: number) => {
    setCheckedTasks(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  if (!classification && !processedContent) {
    return null
  }

  // Helper functions for styling
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      task: 'bg-blue-100 text-blue-800',
      log_entry: 'bg-gray-100 text-gray-800',
      thought: 'bg-purple-100 text-purple-800',
      meeting_note: 'bg-green-100 text-green-800',
      invoice: 'bg-yellow-100 text-yellow-800',
      email: 'bg-indigo-100 text-indigo-800',
      reference: 'bg-teal-100 text-teal-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[type] || colors.other
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[priority] || colors.medium
  }

  const formatLabel = (text: string) => {
    return text.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  // Use processed content data if available, otherwise use classification
  const summary = processedContent?.summary
  const keyPoints = processedContent?.key_points || []
  const extractedTasks = processedContent?.extracted_tasks || []

  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 space-y-3">
      {/* Header with brain icon */}
      <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
        <Brain className="w-4 h-4 text-purple-600" />
        <span>AI Analysis</span>
      </div>

      {/* Classification badges */}
      {classification && (
        <div className="flex flex-wrap gap-2">
          {/* Type badge */}
          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(classification.classification_type)}`}>
            <Tag className="w-3 h-3" />
            {formatLabel(classification.classification_type)}
          </span>

          {/* Priority badge */}
          {classification.priority && (
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(classification.priority)}`}>
              <AlertCircle className="w-3 h-3" />
              {formatLabel(classification.priority)}
            </span>
          )}

          {/* Actionable badge */}
          {classification.is_actionable && (
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              <CheckCircle2 className="w-3 h-3" />
              Actionable
            </span>
          )}

          {/* Confidence indicator */}
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            {classification.confidence}% confidence
          </span>
        </div>
      )}

      {/* Summary */}
      {summary && !compact && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-gray-600 flex items-center gap-1">
            <Lightbulb className="w-3 h-3" />
            Summary
          </div>
          <p className="text-sm text-gray-700 bg-white/50 rounded p-2">
            {summary}
          </p>
        </div>
      )}

      {/* Key points */}
      {keyPoints.length > 0 && !compact && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-gray-600">Key Points</div>
          <ul className="space-y-1">
            {keyPoints.map((point, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-purple-500 mt-1">•</span>
                <span className="flex-1">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Extracted tasks */}
      {extractedTasks.length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-gray-600">Extracted Tasks</div>
          <ul className="space-y-1">
            {extractedTasks.map((task, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                <button
                  onClick={() => toggleTask(index)}
                  className="mt-0.5 text-purple-500 hover:text-purple-600 transition-colors"
                  aria-label={checkedTasks.has(index) ? 'Mark as incomplete' : 'Mark as complete'}
                >
                  {checkedTasks.has(index) ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <Circle className="w-4 h-4" />
                  )}
                </button>
                <span className={`flex-1 ${checkedTasks.has(index) ? 'line-through text-gray-500' : ''}`}>
                  {task}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* PARA suggestions */}
      {classification && (classification.suggested_area || classification.suggested_project) && (
        <div className="space-y-1 pt-2 border-t border-purple-200">
          <div className="text-xs font-medium text-gray-600">PARA Suggestions</div>
          <div className="flex flex-wrap gap-2">
            {classification.suggested_area && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs bg-white/70 text-gray-700">
                <FolderOpen className="w-3 h-3" />
                Area: {classification.suggested_area}
              </span>
            )}
            {classification.suggested_project && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs bg-white/70 text-gray-700">
                <Briefcase className="w-3 h-3" />
                Project: {classification.suggested_project}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Compact summary for compact mode */}
      {compact && summary && (
        <p className="text-xs text-gray-600 line-clamp-2">{summary}</p>
      )}
    </div>
  )
}
