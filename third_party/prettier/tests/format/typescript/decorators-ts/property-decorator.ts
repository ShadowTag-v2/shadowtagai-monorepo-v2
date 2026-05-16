class Greeter {
  @format("Hello, %s") greeting: string;

  constructor(message: string) {
    this.greeting = message;
  }
  greet() {
    const formatString = getFormat(this, "greeting");
    return formatString.replace("%s", this.greeting);
  }
}
