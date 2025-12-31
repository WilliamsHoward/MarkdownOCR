"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Download, FileText, CheckCircle2, Loader2 } from 'lucide-react';

interface MarkdownPreviewProps {
  content: string;
  filename: string;
  isLoading: boolean;
  onDownload: () => void;
}

export const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({
  content,
  filename,
  isLoading,
  onDownload,
}) => {
  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-12 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col items-center justify-center">
        <Loader2 className="w-10 h-10 text-blue-500 animate-spin mb-4" />
        <p className="text-gray-600 font-medium">Generating preview...</p>
      </div>
    );
  }

  if (!content) {
    return null;
  }

  return (
    <div className="w-full max-w-5xl mx-auto mt-8 flex flex-col gap-4">
      <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center">
          <div className="bg-green-100 p-2 rounded-full mr-3">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Conversion Complete</h3>
            <p className="text-xs text-gray-500">{filename.replace('.pdf', '')}.md</p>
          </div>
        </div>

        <button
          onClick={onDownload}
          className="flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Download className="w-4 h-4 mr-2" />
          Download Markdown
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-100 bg-gray-50 px-6 py-3 flex items-center">
          <FileText className="w-4 h-4 text-gray-400 mr-2" />
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Markdown Preview</span>
        </div>

        <div className="p-8 overflow-y-auto max-h-[600px] prose prose-blue prose-slate">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};
