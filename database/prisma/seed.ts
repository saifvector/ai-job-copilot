import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting database seed for AI Job Copilot...');

  // Demo user data for initial environment verification
  const demoEmail = 'alex.chen@example.com';

  const user = await prisma.user.upsert({
    where: { email: demoEmail },
    update: {
      name: 'Alex Chen',
    },
    create: {
      name: 'Alex Chen',
      email: demoEmail,
      profile: {
        create: {
          preferredRoles: [
            'Staff Software Engineer',
            'Full Stack Architect',
            'AI Solutions Engineer',
          ],
          preferredLocations: ['Remote', 'San Francisco, CA', 'New York, NY'],
          yearsOfExperience: 8,
          resumeUrl: 'https://storage.jobcopilot.dev/resumes/alex-chen-sample.pdf',
        },
      },
    },
    include: {
      profile: true,
    },
  });

  console.log(`✅ Seeded demo user: ${user.name} (${user.email}) [ID: ${user.id}]`);
  console.log(`✅ Seeded profile with ${user.profile?.preferredRoles.length} roles, ${user.profile?.yearsOfExperience} years experience.`);
  console.log('✨ Database seeding completed successfully.');
}

main()
  .catch((e) => {
    console.error('❌ Database seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
