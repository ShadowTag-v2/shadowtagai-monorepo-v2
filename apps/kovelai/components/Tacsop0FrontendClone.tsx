import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function Tacsop0FrontendClone() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-lg border-gray-200">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">TACSOP 0 Clone</CardTitle>
            <CardDescription className="text-gray-500">
              Frontend module specification implementation based on TACSOP 0
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium leading-none text-gray-700">
                Email
              </label>
              <Input id="email" type="email" placeholder="Enter your email" className="w-full" />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium leading-none text-gray-700">
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                className="w-full"
              />
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="ghost" className="text-gray-600 hover:text-gray-900 hover:bg-gray-100">
              Cancel
            </Button>
            <Button variant="default" className="bg-blue-600 hover:bg-blue-700 text-white">
              Submit
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
