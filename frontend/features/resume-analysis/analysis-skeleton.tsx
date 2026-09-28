import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/loader';


export const AnalysisSkeleton: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Profile Card Skeleton */}
      <Card className="p-6 border border-border/80">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <Skeleton className="h-16 w-16 rounded-2xl" />
            <div className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <div className="flex items-center gap-3">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-4 w-28" />
              </div>
            </div>
          </div>
          <div className="flex md:flex-col items-start md:items-end gap-2">
            <Skeleton className="h-6 w-32 rounded-full" />
            <Skeleton className="h-4 w-24" />
          </div>
        </div>
      </Card>

      {/* Summary Skeleton */}
      <Card className="border border-border/80">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2.5">
            <Skeleton className="h-8 w-8 rounded-lg" />
            <div className="space-y-1.5">
              <Skeleton className="h-5 w-40" />
              <Skeleton className="h-3.5 w-64" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-20 w-full rounded-lg" />
        </CardContent>
      </Card>

      {/* Skills Skeleton */}
      <Card className="border border-border/80">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Skeleton className="h-8 w-8 rounded-lg" />
              <div className="space-y-1.5">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-3.5 w-72" />
              </div>
            </div>
            <Skeleton className="h-8 w-44 rounded-lg" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-16 w-full rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Experience & Projects Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border border-border/80">
          <CardHeader>
            <Skeleton className="h-6 w-36" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2].map((i) => (
              <Skeleton key={i} className="h-24 w-full rounded-xl" />
            ))}
          </CardContent>
        </Card>

        <Card className="border border-border/80">
          <CardHeader>
            <Skeleton className="h-6 w-36" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2].map((i) => (
              <Skeleton key={i} className="h-24 w-full rounded-xl" />
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
