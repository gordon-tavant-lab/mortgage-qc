We auto-clear some and then the remainder are things that absolutely has to be decision by a human, right? Because the machine can't figure it out for some reason. There's not enough data. They need to look at some other pieces of information. It's not something that's easily understandable. So a human intervention is needed. Those are the only things that they do on the platform and that's it, right? I'm done with this loan.

Let's move on to the next one and next one and next one.

Okay.

I do have a question because during This prototyping, this working on this, there's two aspects that was giving me a lot of fits.

Okay.

The first one is Data extraction, because remember, initially we said we already have a product on that, right?

Yes Yes, yes, yes.

We don't need to build. That was the inaccuracy that was giving me hits because I had to have the accurate information to be able to QC and that was part that is having trouble.

Right Exactly.

So if I could either connect with the existing tool I hate to rebuild it, but that is the part that is the input, right? You know, you have the right input before the output. So that was one big aspect that was causing me fit at the time. The second one is, I need a lot of long data with scenarios that is known, right? Because I just get files, but I don't know what's the problem with it. So when I run, like if it gives me error, I don't know if it's right or wrong.

So if I could either synthetic or whatever, as long as I know, hey, somebody checked on us, this is like, oh, credit score is not enough, or the appraisal is off, right? Then I know, okay, when those rules fire, I know that's working, right? So those two things, I don't have the...

Yeah.

You know, well the first one is not, I don't have, I just don't, I didn't permit the data extraction.

The second one, I really need some expertise and some data. for that because to really run this properly, I need those two.

I agree.

And And then the third one is that these Excel spreadsheet, right, that came from them is it... all we need, like the rule set, or should I go grab the different Fannie Mac selling guy and the other one.

No.

So, That's our base, but we may need additional information to actually implement that base.

Just out.

So that base is, again, when I go through that spreadsheet, it's not clear to me what product programs this needs to fire for. We don't want to run all 800 for every loan that comes in. There has to be a these are required for this product program. If this value for this loan, like for example, if it's owner occupied, then apply these set of rules. If it's an investment loan, apply these set of rules. But they are not similar.

They're two distinct sets. So that information, I think Kayla needs to... get us a little bit more Uh, interpretation and depth and she's trying to meet them, right? So, We may get additional information, but for now, without waiting for those, let's assume that this applies for everything, and then we can structure it later. Okay. For now, for now.

Yeah Okay, okay, okay, yeah.

Okay, so yeah, those two things. And so the data, should I still look for Kayla? I know she's traveling. She's like super busy. So it's tough to be... Okay.

She just came back today.

She'll be available tomorrow. She she was traveling yesterday. Next week are you in? Are you in? You are, right? So. Yeah, you'll have to do this online a lot because He is not going to be there.

Yeah.

And then she's traveling on Thursday for a meeting in Tampa. So again, latter part next week, there will be some travel.

Okay.

You'll be traveling the first part of the week. So let's just do it online.

No problem.

Yeah, no problem.

I don't think it's going to be a... Yeah. But she definitely needs to validate the check itself. Did we interpret the check correctly?

Let's do it for a good subset of those that you can use as a, "Hey, I understand exactly what needs to happen and how that check needs to be implemented, and this is the result that should come out." She told me she was able to get some files done through Cloud.

Yeah.

Is that right?

Yeah, I don't...

Yeah, yeah. She did mention that. And that's where I'm trying to...

Yeah, yeah, yeah.

I guess... Understand, so with that, that might be a lot better path for me because then I don't need to do a document extraction, right? Like, but The key to this is really not, is really How should I say, right? the data from the loan system and the document itself. And you want to not just check them, but compare them that they are both valid, right? So,There is, it is two steps, right? You have the document and extracted the data from it and then you can match. But right now this is the problem with our test.

all the data she's going to provide from the LOI. Hehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehehe fly-t-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-try-tryThat's okay, my kid does that.

So all the loans that she's gonna give me is from the LOS, right? So then that will, that is gonna be totally accurate. So I cannot compare the that test right from the document to the system.

No, we actually we need to consider all three.

We need to consider the potentially have a potentially I don't know for sure right now have a access to the LOS where the loan is residing. the data about the loan is residing.

Yeah.

We may have access to, obviously we'll have documents, that's a given because you're in a QA/QC, you will get a closed loan file that comes back from the title company signed and dated by the borrower. So just to say you're clear, right? This happens after the borrower has signed on the hundreds of documents that they sign at the closing table. So it's a closed loan. It's funded, closed loan. That is now the source of truth.

So that comes back to them. from the title company, they have to unpack that blob of PDFs, which we will do through our document analysis. Okay.

and then give me the result then I could Yeah.

It will give you what kind of documents there are.

It will give you the extraction from certain fields and we may have to expand the extraction because. Expand the extraction because we need more data elements to review. Okay. So that is one exercise and then apply the checks on this.

Apply the checks on the document, on the loan data, in some form, maybe an Excel file, 3.4 file, a MISMO 3.4 file and the LOS. Kevin.

Yeah.

Okay, three of them. Gotcha. May I ask you what the maximum rate is? 3.4 file, the XML file. Nismo, Nismo. Where did they come from?

A mismo, mismo. The MISMO could come from the L potentially could come from the LOS.

Is it from the LOS? Or...

It could be You know what, somebody has to give you some The title company may give you an external file as well. in a MISMO form. So when they send you the documents, they may send you the loan data in a MISMO form. That's the title company, and then you have access to the LOS, and we can export data from there in the 3.4 file, and that's about it. Those three should be it.

Okay.

Okay. So, I meet with the architect, I could ask to have some documents.

Those three should be it.

Because see, this is the hard part, right? We will have to deal with real documents because it has to go through the scanning. Right? Or do we You know, that's where I'm at, right? If we do synthetic, we have to make synthetic for three different versions.

Yeah To get that, you see...

Let's not try to attack Um. All the parts of the problem. Let's attack the problem. The what this tool is supposed to be really good at at the core, which is I have 800 checks that I need to do. I have three sources of data. Can I apply correctly and give you a good result set? Let's. Solve for that first. The core of the problem. Right? The ability to extract documents, the data from the documents, we can give it to the touchless team.

Yeah.

Like, look, I'm going to give you a document blob. Your job is to make sure it goes through the document analysis tool and gives me this data back. and the classification of the documents back because it has to go through that.

Yeah.

Yeah. Yeah.

We're not building that. So assume that that is there. Don't solve for that.

Yes.

And then for the agent, the tool into the LOS, That we should have a connector too. We have a way into the LoS today, we can reuse that. All right. The main thing that let's focus on is if I have the document gone through document analysis and I have the document data in some format, I have the MISMO data, I have the files 3.4 data, let's say, and I have the...

Um, Then I apply the rules. Right?

And my output, the rules run fast. Rules figures, it's an intelligent run of the tool. So it figures out, oh, this is a product and program, so these are the set of rules that I need to run. It interprets it correctly. So whether we think through the implementation, are we going to have a rule deterministic? Are we going to have an agent that interprets the thing and then runs however it wants, right?

It's a design question we should go go through quickly I would lean towards deterministic because we don't want this to, "Hey, I thought about it and I ran it this way, but next time I ran it another way." You don't want that. There's one interpretation for this. If our tool generates a set of rules that it runs all the time and that's what it runs, compiles, it's like a compiling stage.

Um, Think about that.

Okay.

Okay.

No, no. I wanted to do that, yeah. But this will Fundamentally be different than the POC because I think what Olof built is very LLM.

Think about how do I apply the rules? Think about how do I present a configurable pattern for them to create the rules? And then think about how do I output the result set so it's very quick for a person to mitigate the outcome of the result set.

Those are the areas that let's focus on, right?

centric, how it interprets Hold it.

Rather than, oh, let me solve the extraction problem. Let me solve the integration problem. Yeah. Yeah.

I I'm not. I'm not suggesting the design. I'm just saying that.

Even if it's an LLM, it has to be deterministic.

Okay.

We can't just say, oh, you figure it out and I'll accept what you give me. You see my point, right? Even if we were to adhere to that design, that LLM would have to give me the right checks and the right results set every time.

Oh, of course. Of course. I get that.

Yes.

Okay.

It couldn't have been like, "We can't put an asterisk, LLM use so there may be mistakes." We can't do that. The I is use, so assume, validate yourself. It's like, "Yeah, I gave you the tool is supposed to validate for me." Right?

Okay.

So that's what I'm saying. It's like, let's design it in a way where it's The outcome of it is highly deterministic. It's not highly, it is deterministic. And that may entail that we regimen the tool in a way where the LLM is always deterministic or the LLM generates, right? At the point of when we run, it generates, not at the run, when we configure a set of QA, QC checks, it generates a set of rules that we can validate against and agree to and test.

And then that is what we run, right? Next time we have an update, we take it through the pipeline. it updates the rule, and then we run the rules. Um, Olav may come into the picture and say, look, I am so confident that LLMs can repeat their behavior that yes, you shouldn't do an intermediate rules, right? generation. It can run it. I have heard him say that a couple of times, but I... It's like, I have no way of validating that.

Yeah, we need some tests, right?

I did started a, before I jumped on using OLOF, I did, build a LLM interpreter, basically taking those rules, basically taking what you said was converted to those Drew's rules set. So then it's basically just a rule engine right afterward. So I did have something like that, but it wasn't...

Yeah, yeah, yeah.

Fully. It's just that it was just converting the rules. That wasn't like all this citation or these display all this stuff. So maybe I could build on that. But what I want to do is just. Yeah, go ahead.

Right, right.

can discuss and debate what the design of this is, right? Whether we have an intermediate rule set or whether we go directly from creating that route with the set of blocks and the blocks are set of checks and the checks are interpreted by an LLM because There's multiple factors involved. Factor 1 of the design is, You have to prove to me that I run the same check every time. Regardless of the loan that goes through, it won't give me a pass one time and a fail another. That's one.

The other thing is maybe if we generate the intermediate rules, I don't have the cost of the LLM run every time.

Mm hmm.

Yes. Yes, that's a big one.

Right? And that's a big, it might turn out to be a big cost if it's like thousands and thousands of loans that we run this against, right?

Mm-hmm, mm-hmm.

I can't judge because I don't know what the token cost is going to be per file right now. If it's like one cent per file, nobody cares. But if it's like a couple of dollars per file, everybody will care, right? Because we could have 10,000 files. every run is going to cost me $10,000. No. Those are the things that we really need to factor in to our design decision. Um, And then the ability to And we have to kind of make it easy for them to configure. Right now, the way Olaf built it is very easy to understand. I have these routes. The routes are composed of blocks. The blocks I can create just by wiring it together. I can put checks within these blocks.

Beautiful. I know exactly how to configure something and have a loan run through it. I think that is what, by the way, is what caught their attention. They're like, "Wow, I can use this tool to configure a very simple thing or I can create the configure this tool to run a very complex thing. It's up to me. I do it. The BA, the business analyst or the subject matter expert can build this out and run files against.

I don't need to go back to my IT." That caught their imagination. I can see it in their face. Okay.

He mentioned that again today too, David.

Yeah, yeah, yeah.

Oh, he did. Okay, okay, okay.

He said he wants his non-technical folks to be able to configure this easily. And so we heard that loud and clear. Yeah.

Beautiful, beautiful.

So I don't want to stray away from the philosophy of the tool. Which is these routes and blocks and checks and these come together and ability for them to run at a demand and run at a whim against a target set. look, we have a nice seed. We need to make this-turn this into a product. So that's the exercise we'll have to go through. One thing you could potentially do start with Gordon is kind of all the stuff that we talked about. Let's document them.

Right. Like, Each in each area. Here's the input into. Here's the tool. Here's the tool processing. Here's the tool design. LLM versus non-LLM. Intermediate rules, not intermediate rules. Output. What do we do with the output? What tentacles does it have, right? Does it have to go and talk to the LOS, other systems, right? I have to talk to touchless for the document analysis piece. Where do I send the results set to?

So just start creating a kind of a PRD, a product requirement doc, right? Let's put that together, ask all the questions that we need to answer.

Yeah.

Yeah.

Between the three of you and Kayla, let's try to get this done quickly within the next month, okay?

Okay, I do have two other outside questions I'd like to ask.

I never used theVerse two, so I didn't realize you left a message to me a while back.

Yeah, yeah, yeah. Thank you.

Oh, what was it?

The expense one Yeah.

Do you remember? I can't. Did I reject something or what did I do?

Yeah, yeah, yeah, because it said it needs receipt and then I think some of them is over 60 days now.

So put them in.

So I didn't realize that. So I don't know how that, What?

Just make sure that every one of those line items, if it's above, I believe if it's above $10. Right. If you have the receipt and it's above ten dollars, you absolutely put it in. If it's below ten dollars, you have the receipt, put it in. But it's not absolutely necessary. OK. And the time frame is 60 days.

Okay.

But I think there is a bunch that is over 60 days now.

So do not put in, you know, just keep up to date on the month, monthly.

I wonder how is it going to be a problem? That's not a lot. Maybe five, ten ones.

We'll just get an exception from our CFO.

So Saj Sasha.

What's his name? Okay.

Yeah.

Session. Session. We can get an exception that say, hey, Gordon didn't know the rules and it went overboard for a couple of things. He'll make an exception on that one. So put those in. Do not hold those back. Put them in as soon as possible. But did I reject the whole thing or reject one line item?

Okay.

Okay. Yeah. No, the whole thing, the whole thing. And then I didn't realize till I recently saw, cause I was, I see the penny on my, okay, I'm waiting. And then I I check in again and I was like, oh, that's a little note. button there and then I'm like, oh, I didn't even see the little button that said message. So, yeah, I will... Add all those stuff in.

Got you.

Oh, okay.

Let me let me see once I once I put it back to you. I don't think I get to see it anymore, but. Give me a minute. Let me just see what's in my queue.

Oh, you took it up. Okay.

It's not as in draft now because I took it off and tried to... I'm going to add the receipt and I'll submit it within a day or so.

OK, 2S89. Give me a minute to...

Yeah, I can't see it anymore because I I put it back.

Okay.

Okay. I will add the stuff and submit it again that way Yeah, because I have the receipt.

Yeah, it's not the credit card.

Because I thought connected to the credit card, that should be it. But I realized I need to... Okay.

It's a it's a you need the receipt. OK, so keep the receipt all always. As I mentioned, if it's. Sometimes they let the $10 and below, they let them go, but sometimes they ask for it. So if you have it, attach it. Yeah.

Okay, I'm... Okay, I have most of it.

That's fine. And even if it goes above 60 for you, just put them in because this is the first time you're submitting.

I might miss a few of them. So I hope it's okay this time.

Okay.

So timelines will make an exception for it. I'll put in a note to Sesha and Anusha. Anusha is the person who processes them in India. I'll tell her that this make an exception because Gordon is new and, you know, he's putting this in for the first time.

Okay. Okay. And the last one is I submitted a PTO for next week, two days after the summit. Just Thursday, Friday if it's okay to approve that.

Oh wait wait let me okay okay let me just take a look.

Yeah, sure.

The system rebooted everything is I have to bring up everything from scratch.

When you go in, does it give you hours that you have accrued or no?

Yeah, it does, it does, yeah.

I have enough. Yes, yes, I have 35 or so.

Does it show you that you have 16 hours accrued?

Okay, okay, then it's no problem at all.

Thursday and Friday, yeah.

I just want to make sure that you have enough hours in your bag to pull out and use. You're just using 25th and 26th, which is next week, right?

Yeah. Thank you.

Thursday and Friday.

Perfect. No problem. I just approve it. You should. Yeah.

And if you have... Yeah, thank you.

And if you have time, the one last thing is to check with you. How am I doing and if there's anyone I need to talk to or connect with or or anything I need to look into, like learn or...

Just.

Yeah, it's the things that we know.

If any advice and thus especially If any advice and thus especially All right, yeah, it makes sense.

I think you're good. Just a couple of things on on. deep dive into the mortgage domain, right? So the more you understand mortgages and all the speak that we give on the mortgage side. So Sujata has Mortgage 101 and courses around Tavon Mortgage University, things like that, that you can take to get up to speed on mortgage, mortgage process, the lingo. What do we do in underwriting, right? At the depth of knowledge that you can intelligently talk about and say, hey, this agent can autonomously decide this, right? But what is it deciding?

It's like if, for example, when it comes to income analysis, Everything is determined, right? You decide this is a W-2 wage earner because so he's an employee of some company. This is a self-employed person. This is a gig economy. They work for themselves, you know, sometimes and they'll get a very... you know, an undetermined number every day or every week or every month. And so there's There's a ways to compute this, there's ways to compute this, there's ways to compute this. Now, does an agent really come into this picture?

no need because if I know what the areas that they work in, what kind of jobs they're doing, and I have the data, there's an algorithm that I can just apply to get the qualified income. It's not an agent trying to think through this. Now, there may be scenarios, maybe scenarios where it's not clear, there is no algorithm, and then some underwriter comes in and tries to figure it out, and we can apply a genetic capability there, right?

Autonomous capability there. But those are the nuances that I want you to get to know, right? And you can talk intelligently about and say, look, there are certain cases that it makes sense for an agentic capability to die. I mean, in certain cases, you don't want it to come in because you want that complete utter determinism. You know exactly how it was calculated. You know exactly the equations that were applied because the Your regulator on top is going to audit you, and if they don't understand how you calculated that number, you are dead.

Okay, you will buy that loan, right?

And you don't get to know this unless you understand mortgage and domain and go in-depth into all this. As much as you can try to get to know the domain through all the courses that Sujata would have. The other thing I would do just kind of company-wise is expand your reach, right?

Yeah. Okay.

Okay. Thank you.

So offshore. Who are on the offshore side? Amit and Vardaraj and that group on the Tavante Eye side. And then our product engineering product head side, right? Who are the BAs? Who are the heads of products? And I'll introduce you to them.

But, you know, get to know them. Get to talk to them. I'll introduce you to Monish. Get to know him. The type of work I'm expecting to do kind of partly is actually help develop some of the products as a prototype. You developed the A great example would be what we're working on right now. Like we prototype it and then we hand it off to them to make it real, right? Industrial strength, enterprise, guardrails, security, right? You build out the title review part, the title analysis component as a prototype, and you work with Kayla and say, hey, it works. You know, this is how it should be.

Hand it off to Monish and team and say, okay, now take it of the touchless framework, right?

Okay.

Cool.

Give it its observability, give it its monitoring, give it its auditability, the logging capability, all that. I don't want to get into that. I need to do the demos. I need to create prototypes. So we hand it off to them. So I want you to become a big part of that. A lot of the things that we will think...

I had this even in yesterday when we were talking to the citizens guy.

There's some ideas he threw at us and it's like, hey, if we could prototype that very quickly and show it to him, he will go with us because he says nobody in the industry is doing it.

I can't give it to Monish because his team will take forever. They do the production rollout. Kayla will work with you on doing some of that, prototyping it, making sure it works. We want to show it to him.

Okay.

I said, is this what you meant?

Okay. Okay.

It's like you gave us something. We took it, understood it, interpreted it, and built this out. But is this really what you meant? So that the prototype quickly, a quick prototype will...

have us show this to him and get the right direction, right? Once we get the right direction, then we can say, okay, now Manish and team build it out as part of the platform. Okay. So yeah, my guidance would be just get, so two things, one deep dive into mortgage, number two, deep dive into the company and the people that you need to kind of work with. Um, And then oh yeah, so so I talked to Sandeep.

Okay.

Okay.

I'm thinking that this housing wire AI one let Olaf do that that. Peace. Right following that, I think in September, October timeframe, there's another called Mortgage AI that happens in California.

Okay. Okay.

let's shoot for something different there that you can present.

It'll be potentially a keynote. I want that HousingWire AI Summit format to be like a talk theory principles and then show an example, right? Through code, through here's the workbench, here's how you do the workbench, here's let me take you through the journey of the tool, right? it really resonated last time because people understood the theory, the practice of like, okay, here's what he's trying to do conceptually. And then he's actually showing it to me, right?

And he's showing me the tool and how the...

Cool.

The proof, right? And in...

Like this example that we did for David, Angie and team, the QA/QC tool, it would be a perfect example of look, here's the 800 thing that they gave us, here's the process we followed, and out of it came a tool that allows you to configure these rules, et cetera, et cetera, and see, look, it works. right?

Oh.

Principle, concepts, theory, framework, and then actually showing a tool. So for the Mortgage AI Conference, I want you to kind of think about something. This is a little bit out. So and really, really maybe on the autonomous side. Maybe we can work together on a true autonomous agentic capability where We give, I don't know right now, I'm just giving some examples, but something truly autonomous, right?

If they see, it would be like the agent did what a human would have done. Right. Maybe the governance thing is done. There's a lot of people who understand, yeah, I have to do that and then I'm done. But maybe in October, we should dazzle them with something. Right? Something that is something that, you know, up to now, I have not seen A true example of autonomous decisioning. Right.

Okay, I like that.

Yeah, we getting there. We have the Fable now. This is why I'm so excited that it could be the time where this comes along.

Maybe it'll come through and we can figure out a use case Where we can really show autonomous thinking, right?

All right. Okay.

We didn't program it to do this. It looked at what came to it and it figured out within guardrails, figured out that these are the steps to fixing this like a human would. And it did the right thing.

Yeah, okay.

Okay. So think, I mean, we have time, right? July, August, September, three months. Let's build something that is truly like, wow. Wow, right? In the mortgage industry.

Okay.

Okay.

Yeah.

Let's figure this out.

Okay. I like that. Also, I'll work with you on that. I like that. Okay.

I mean, we have some time. Let's throw some ideas around, include Sandeep, include others, right, Olav and others. And just like, hey, what is it that really would wow the people there? It was like, what is it that's something that if we show they will understand the power of true autonomous AI, right?

Okay.

Right, yes.

Okay.

I would love that.

So let's do that. Okay. All right, sounds good.

Okay. No, it's not, yeah. Excellent. Hey, thanks. Nice to see you. Okay.

Thank you. Absolutely.

Let's schedule these once in a while, right?

So then we can keep in touch. Cool. We will see you at the summit. Sounds good. Take care. Thanks.

I love that. Okay. And I'll see you at the summit for a little bit. Hehe. Okay, see ya.