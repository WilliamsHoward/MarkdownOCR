"use client";

import React, { useState, useEffect, useCallback } from "react";
import { FileUpload } from "@/components/FileUpload";
import { MarkdownPreview } from "@/components/MarkdownPreview";
import {
  getTaskStatus,
  getMarkdownContent,
  downloadMarkdown,
  TaskStatus,
} from "@/lib/api";
import { FileText, Github, Layers, Zap, CheckCircle2 } from "lucide-react";

export default function Home() {
  const [activeTask, setActiveTask] = useState<{
    id: string;
    filename: string;
  } | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [markdownContent, setMarkdownContent] = useState<string>("");
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const pollStatus = useCallback(async (taskId: string) => {
    try {
      const status = await getTaskStatus(taskId);
      setTaskStatus(status);

      if (status.status === "completed") {
        setIsPreviewLoading(true);
        const content = await getMarkdownContent(taskId);
        setMarkdownContent(content);
        setIsPreviewLoading(false);
        return true; // Stop polling
      }

      if (status.status === "failed") {
        return true; // Stop polling
      }

      return false; // Continue polling
    } catch (error) {
      console.error("Error polling status:", error);
      return true; // Stop polling on error
    }
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (
      activeTask &&
      (!taskStatus ||
        (taskStatus.status !== "completed" && taskStatus.status !== "failed"))
    ) {
      intervalId = setInterval(async () => {
        const shouldStop = await pollStatus(activeTask.id);
        if (shouldStop) {
          clearInterval(intervalId);
        }
      }, 2000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [activeTask, taskStatus, pollStatus]);

  const handleUploadSuccess = (taskId: string, filename: string) => {
    setActiveTask({ id: taskId, filename });
    setTaskStatus(null);
    setMarkdownContent("");
  };

  const handleDownload = () => {
    if (activeTask) {
      downloadMarkdown(activeTask.id, activeTask.filename);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 tracking-tight">
              MarkDown OCR
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium text-gray-500">
            <a href="#" className="hover:text-blue-600 transition-colors">
              Documentation
            </a>
            <a
              href="#"
              className="flex items-center gap-1 hover:text-gray-900 transition-colors"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-white border-b border-gray-100 py-12 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
            Convert PDFs to Markdown with{" "}
            <span className="text-blue-600">Local AI</span>
          </h1>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            High-quality OCR using Ollama and LM Studio. Preserve tables, math
            formulas, and code blocks while keeping your data private on your
            own machine.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span>Fast local processing</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
              <Layers className="w-4 h-4 text-blue-500" />
              <span>Format preservation</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>100% Private & Secure</span>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="flex-grow container mx-auto px-6 py-12">
        {!activeTask || taskStatus?.status === "failed" ? (
          <div className="space-y-8 animate-in fade-in duration-500">
            <FileUpload onUploadSuccess={handleUploadSuccess} />

            {taskStatus?.status === "failed" && (
              <div className="max-w-2xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                <strong>Error:</strong>{" "}
                {taskStatus.error ||
                  "Conversion failed. Please try again with a different model or settings."}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            {/* Progress Card */}
            {taskStatus && taskStatus.status !== "completed" && (
              <div className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-semibold text-gray-900">
                    Processing Document
                  </h3>
                  <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-1 rounded uppercase tracking-wider">
                    {taskStatus.status}
                  </span>
                </div>

                <div className="w-full bg-gray-100 rounded-full h-2.5 mb-2">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                    style={{
                      width: `${taskStatus.total_pages > 0 ? (taskStatus.current_page / taskStatus.total_pages) * 100 : 5}%`,
                    }}
                  ></div>
                </div>

                <div className="flex justify-between text-sm text-gray-500">
                  <span>{activeTask.filename}</span>
                  <span>
                    {taskStatus.total_pages > 0
                      ? `Page ${taskStatus.current_page} of ${taskStatus.total_pages}`
                      : "Initializing..."}
                  </span>
                </div>

                <div className="mt-8 flex justify-center">
                  <button
                    onClick={() => setActiveTask(null)}
                    className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    Cancel and start over
                  </button>
                </div>
              </div>
            )}

            {/* Preview Section */}
            <MarkdownPreview
              content={markdownContent}
              filename={activeTask.filename}
              isLoading={isPreviewLoading}
              onDownload={handleDownload}
            />

            {taskStatus?.status === "completed" && (
              <div className="flex justify-center pt-8">
                <button
                  onClick={() => {
                    setActiveTask(null);
                    setTaskStatus(null);
                    setMarkdownContent("");
                  }}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Convert another file
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-500 text-sm">
          <p>
            © {new Date().getFullYear()} MarkDown OCR. Powered by Local LLMs.
          </p>
        </div>
      </footer>
    </div>
  );
}
