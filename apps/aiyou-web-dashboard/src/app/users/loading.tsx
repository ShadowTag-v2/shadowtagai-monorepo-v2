export default function LoadingUsers() {
  return (
    <div className="space-y-4 p-4">
      {/* Title Placeholder */}
      <div className="h-8 w-48 bg-gray-200 rounded animate-pulse"></div>

      {/* List of 5 fake "User" rows to reserve vertical space */}
      <div className="space-y-3 mt-6">
        {[1, 2, 3, 4, 5].map((id) => (
          <div key={`skeleton-${id}`} className="flex items-center space-x-4 p-3 border rounded-lg">
            {/* Fake Avatar/ID block */}
            <div className="h-12 w-12 bg-gray-200 rounded-full animate-pulse"></div>
            {/* Fake Text lines */}
            <div className="space-y-2 flex-1">
              <div className="h-4 w-1/3 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-3 w-1/4 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
