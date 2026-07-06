import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { marked } from 'marked';

// Define the base path for content, relative to apps/web execution root
const CONTENT_DIR = path.join(process.cwd(), '../../content');

export interface BlogPost {
  title: string;
  slug: string;
  excerpt: string;
  publishDate: string;
  tags: string[];
  readingTime: number;
  featured: boolean;
  draft: boolean;
  contentHtml: string;
}

export interface Project {
  title: string;
  slug: string;
  tagline: string;
  status: 'active' | 'complete' | 'archived' | 'planned';
  featured: boolean;
  thumbnail: string;
  techStack: string[];
  category: 'saas' | 'open-source' | 'tool' | 'experiment';
  liveUrl?: string;
  githubUrl?: string;
  startDate: string;
  publishDate: string;
  contentHtml: string;
  timeline?: string[];
  challenges?: { title: string; content: string }[];
}

export interface LabExperiment {
  id: string;
  title: string;
  slug: string;
  tagline: string;
  status: 'live' | 'wip' | 'paused' | 'failed' | 'completed';
  category: string;
  tags: string[];
  hypothesis: string;
  publishDate: string;
  githubUrl?: string;
  contentHtml: string;
}

// Memory caching containers
let cachedBlogPosts: BlogPost[] | null = null;
let cachedProjects: Project[] | null = null;
let cachedExperiments: LabExperiment[] | null = null;

const cachedBlogPostBySlug: Record<string, BlogPost | null> = {};
const cachedProjectBySlug: Record<string, Project | null> = {};
const cachedExperimentBySlug: Record<string, LabExperiment | null> = {};

// Calculate reading time in minutes
function calculateReadingTime(text: string): number {
  const wordsPerMinute = 200;
  const words = text.trim().split(/\s+/).length;
  return Math.ceil(words / wordsPerMinute);
}

// Read Markdown content from a directory
function getItemsFromDirectory<T>(subdir: string, mapper: (slug: string, data: any, content: string) => T): T[] {
  const dirPath = path.join(CONTENT_DIR, subdir);
  
  if (!fs.existsSync(dirPath)) {
    return [];
  }

  const files = fs.readdirSync(dirPath);
  
  return files
    .filter(file => file.endsWith('.md'))
    .map(file => {
      const slug = file.replace(/\.md$/, '');
      const fullPath = path.join(dirPath, file);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const { data, content } = matter(fileContents);
      return mapper(slug, data, content);
    });
}

// Get single item by slug
function getItemBySlug<T>(subdir: string, slug: string, mapper: (slug: string, data: any, content: string) => T): T | null {
  const dirPath = path.join(CONTENT_DIR, subdir);
  const fullPath = path.join(dirPath, `${slug}.md`);

  if (!fs.existsSync(fullPath)) {
    return null;
  }

  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, content } = matter(fileContents);
  return mapper(slug, data, content);
}

/* ==========================================================================
   BLOG / JOURNAL
   ========================================================================== */

const mapBlogPost = (slug: string, data: any, content: string): BlogPost => {
  const contentHtml = marked.parse(content) as string;
  return {
    slug,
    title: data.title || 'Untitled Post',
    excerpt: data.excerpt || '',
    publishDate: data.publishDate || new Date().toISOString().split('T')[0],
    tags: data.tags || [],
    readingTime: calculateReadingTime(content),
    featured: !!data.featured,
    draft: !!data.draft,
    contentHtml,
  };
};

export function getBlogPosts(): BlogPost[] {
  if (cachedBlogPosts) return cachedBlogPosts;
  cachedBlogPosts = getItemsFromDirectory('blog', mapBlogPost)
    .filter(post => !post.draft)
    .sort((a, b) => b.publishDate.localeCompare(a.publishDate));
  return cachedBlogPosts;
}

export function getBlogPostBySlug(slug: string): BlogPost | null {
  if (cachedBlogPostBySlug[slug] !== undefined) {
    return cachedBlogPostBySlug[slug];
  }
  const post = getItemBySlug('blog', slug, mapBlogPost);
  if (post?.draft) {
    cachedBlogPostBySlug[slug] = null;
    return null;
  }
  cachedBlogPostBySlug[slug] = post;
  return post;
}

/* ==========================================================================
   PROJECTS
   ========================================================================== */

const mapProject = (slug: string, data: any, content: string): Project => {
  const contentHtml = marked.parse(content) as string;
  return {
    slug,
    title: data.title || 'Untitled Project',
    tagline: data.tagline || '',
    status: data.status || 'active',
    featured: !!data.featured,
    thumbnail: data.thumbnail || '/images/projects/placeholder.jpg',
    techStack: data.techStack || [],
    category: data.category || 'tool',
    liveUrl: data.liveUrl,
    githubUrl: data.githubUrl,
    startDate: data.startDate || '',
    publishDate: data.publishDate || '',
    contentHtml,
    timeline: data.timeline || [],
    challenges: data.challenges || [],
  };
};

export function getProjects(): Project[] {
  if (cachedProjects) return cachedProjects;
  cachedProjects = getItemsFromDirectory('case-studies', mapProject)
    .sort((a, b) => b.publishDate.localeCompare(a.publishDate));
  return cachedProjects;
}

export function getProjectBySlug(slug: string): Project | null {
  if (cachedProjectBySlug[slug] !== undefined) {
    return cachedProjectBySlug[slug];
  }
  const project = getItemBySlug('case-studies', slug, mapProject);
  cachedProjectBySlug[slug] = project;
  return project;
}

/* ==========================================================================
   LABS / EXPERIMENTS
   ========================================================================== */

const mapLabExperiment = (slug: string, data: any, content: string): LabExperiment => {
  const contentHtml = marked.parse(content) as string;
  return {
    slug,
    id: data.id || 'EXP-X',
    title: data.title || 'Untitled Experiment',
    tagline: data.tagline || '',
    status: data.status || 'wip',
    category: data.category || 'AI',
    tags: data.tags || [],
    hypothesis: data.hypothesis || '',
    publishDate: data.publishDate || '',
    githubUrl: data.githubUrl,
    contentHtml,
  };
};

export function getExperiments(): LabExperiment[] {
  if (cachedExperiments) return cachedExperiments;
  cachedExperiments = getItemsFromDirectory('experiments', mapLabExperiment)
    .sort((a, b) => b.publishDate.localeCompare(a.publishDate));
  return cachedExperiments;
}

export function getExperimentBySlug(slug: string): LabExperiment | null {
  if (cachedExperimentBySlug[slug] !== undefined) {
    return cachedExperimentBySlug[slug];
  }
  const experiment = getItemBySlug('experiments', slug, mapLabExperiment);
  cachedExperimentBySlug[slug] = experiment;
  return experiment;
}

