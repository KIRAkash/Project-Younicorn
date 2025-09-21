import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  if (!date) return "N/A"
  
  const dateObj = new Date(date)
  if (isNaN(dateObj.getTime())) return "Invalid Date"
  
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(dateObj)
}

export function formatDateTime(date: string | Date): string {
  if (!date) return "N/A"
  
  const dateObj = new Date(date)
  if (isNaN(dateObj.getTime())) return "Invalid Date"
  
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(dateObj)
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const target = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - target.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return "just now"
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes === 1 ? "" : "s"} ago`
  }

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours === 1 ? "" : "s"} ago`
  }

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays === 1 ? "" : "s"} ago`
  }

  return formatDate(date)
}

export function formatCurrency(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatNumber(number: number): string {
  return new Intl.NumberFormat("en-US").format(number)
}

export function formatPercentage(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes"
  
  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

export function getScoreColor(score: number): string {
  if (score >= 8) return "text-success-600"
  if (score >= 6) return "text-warning-600"
  if (score >= 4) return "text-yellow-600"
  return "text-danger-600"
}

export function getScoreBackgroundColor(score: number): string {
  if (score >= 8) return "bg-success-50 border-success-200"
  if (score >= 6) return "bg-warning-50 border-warning-200"
  if (score >= 4) return "bg-yellow-50 border-yellow-200"
  return "bg-danger-50 border-danger-200"
}

export function getScoreLabel(score: number): string {
  if (score >= 8) return "Excellent"
  if (score >= 6) return "Good"
  if (score >= 4) return "Fair"
  return "Poor"
}

export function getInvestmentRecommendationColor(recommendation: string): string {
  switch (recommendation.toLowerCase()) {
    case "strong buy":
      return "text-success-700 bg-success-100 border-success-300"
    case "buy":
      return "text-success-600 bg-success-50 border-success-200"
    case "hold":
      return "text-warning-600 bg-warning-50 border-warning-200"
    case "pass":
      return "text-danger-600 bg-danger-50 border-danger-200"
    default:
      return "text-muted-foreground bg-muted border-border"
  }
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case "new":
      return "text-blue-600 bg-blue-50 border-blue-200"
    case "reviewing":
      return "text-yellow-600 bg-yellow-50 border-yellow-200"
    case "shortlisted":
      return "text-success-600 bg-success-50 border-success-200"
    case "rejected":
      return "text-danger-600 bg-danger-50 border-danger-200"
    case "watching":
      return "text-purple-600 bg-purple-50 border-purple-200"
    case "invested":
      return "text-minerva-600 bg-minerva-50 border-minerva-200"
    default:
      return "text-muted-foreground bg-muted border-border"
  }
}

export function getAnalysisStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case "pending":
      return "text-yellow-600 bg-yellow-50 border-yellow-200"
    case "in_progress":
      return "text-blue-600 bg-blue-50 border-blue-200"
    case "completed":
      return "text-success-600 bg-success-50 border-success-200"
    case "failed":
      return "text-danger-600 bg-danger-50 border-danger-200"
    case "cancelled":
      return "text-muted-foreground bg-muted border-border"
    default:
      return "text-muted-foreground bg-muted border-border"
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + "..."
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

export function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function camelToTitle(str: string): string {
  return str
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (str) => str.toUpperCase())
    .trim()
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text)
  } else {
    // Fallback for older browsers
    const textArea = document.createElement("textarea")
    textArea.value = text
    textArea.style.position = "fixed"
    textArea.style.left = "-999999px"
    textArea.style.top = "-999999px"
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    return new Promise((resolve, reject) => {
      if (document.execCommand("copy")) {
        resolve()
      } else {
        reject(new Error("Copy to clipboard failed"))
      }
      document.body.removeChild(textArea)
    })
  }
}
