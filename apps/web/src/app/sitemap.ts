import { getBlogPosts, getProjects, getExperiments } from '@/lib/content';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://buildwithpnj.in';

  // 1. Define static routes
  const staticRoutes = [
    '',
    '/about',
    '/projects',
    '/journal',
    '/contact',
    '/mission-control',
    '/labs',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date().toISOString().split('T')[0],
    changeFrequency: 'daily' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  // 2. Fetch dynamic journal post routes
  const posts = getBlogPosts();
  const journalRoutes = posts.map((post) => ({
    url: `${baseUrl}/journal/${post.slug}`,
    lastModified: post.publishDate || new Date().toISOString().split('T')[0],
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }));

  // 3. Fetch dynamic project routes
  const projects = getProjects();
  const projectRoutes = projects.map((project) => ({
    url: `${baseUrl}/projects/${project.slug}`,
    lastModified: project.publishDate || new Date().toISOString().split('T')[0],
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }));

  // 4. Fetch dynamic lab experiment routes
  const experiments = getExperiments();
  const labRoutes = experiments.map((exp) => ({
    url: `${baseUrl}/labs/${exp.slug}`,
    lastModified: exp.publishDate || new Date().toISOString().split('T')[0],
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }));

  return [...staticRoutes, ...journalRoutes, ...projectRoutes, ...labRoutes];
}
