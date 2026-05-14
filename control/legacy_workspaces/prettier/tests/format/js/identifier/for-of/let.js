for ((let) of foo);
for (foo of let);
for (foo of let.a);
for (foo of let[a]);
for (let.a of foo);
for (const [a] of foo);
for ((let)().a of foo);
for (letFoo of foo);

for (let.a in foo);
for (const [a] in foo);

for (const of of let);
