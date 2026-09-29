import re

def render():
    page = """import Link from "next/link";
import Image from "next/image";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "FindMyShots Studio" as string,
};

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FFFFFF] font-host text-[#313131] overflow-x-hidden">
      <div className="w-full max-w-[1728px] mx-auto relative">
        {/* Navigation */}
        <header className="flex items-center justify-between px-[58px] pt-[49px] pb-[16px] w-full relative z-50">
          <Link href="/">
            <Image src="/brand/logo.svg" alt="FindMyShots Studio" width={154} height={26} priority />
          </Link>
          <nav className="hidden md:flex items-center gap-[26px] text-[18px]">
            <Link href="#events" className="hover:text-[#FF6100]">Events</Link>
            <Link href="#pricing" className="hover:text-[#FF6100]">Pricing</Link>
            <Link href="/signin" className="hover:text-[#FF6100]">Sign In</Link>
            <div className="w-[13px]"></div>
            <Link href="/signup" className="px-[19px] py-[3px] bg-[#FF6100] text-white rounded-full font-medium">Get Started</Link>
          </nav>
        </header>

        {/* Desktop Absolute Container (Hidden on small screens for simplicity if we strictly want pixel-perfect desktop. But we will make it responsive by using Flex layout with exact margins for desktop.) */}
        <main className="flex-grow w-full relative pb-[200px]">
          
          {/* Collage Section */}
          <section className="relative w-full flex flex-col items-center mt-[14px]">
            {/* Collage Container */}
            <div className="relative w-[1334px] h-[777px] hidden lg:block ml-[72px]">
              {/* Translated left by approx 183 - (1728-1334)/2 = 183 - 197 = -14. So slightly off center. We will just use absolute positioning inside a centered container. */}
              
              <Image src="/marketing/hero/photo-01.png" alt="" width={234} height={268} className="absolute rounded-[16px] object-cover" style={{left: 887+28, top: 63}} />
              <Image src="/marketing/hero/photo-02.png" alt="" width={279} height={322} className="absolute rounded-[16px] object-cover" style={{left: 116+28, top: 123}} />
              <Image src="/marketing/hero/photo-03.png" alt="" width={262} height={302} className="absolute rounded-[16px] object-cover" style={{left: 898+28, top: 233}} />
              <Image src="/marketing/hero/photo-04.png" alt="" width={240} height={427} className="absolute rounded-[16px] object-cover" style={{left: 391+28, top: 35}} />
              <Image src="/marketing/hero/photo-05.png" alt="" width={254} height={320} className="absolute rounded-[16px] object-cover" style={{left: 578+28, top: 107}} />
              <Image src="/marketing/hero/photo-06.png" alt="" width={183} height={221} className="absolute rounded-[16px] object-cover" style={{left: 763+28, top: 174}} />
              <Image src="/marketing/hero/photo-07.png" alt="" width={184} height={227} className="absolute object-cover" style={{left: 228+28, top: 372}} />
              <Image src="/marketing/hero/photo-08.png" alt="" width={299} height={201} className="absolute object-cover" style={{left: 776+28, top: 427}} />
              <Image src="/marketing/hero/photo-09.png" alt="" width={347} height={279} className="absolute object-cover" style={{left: 958+28, top: 83}} />
              <Image src="/marketing/hero/photo-10.png" alt="" width={274} height={304} className="absolute object-cover" style={{left: 0+28, top: 43}} />
              <Image src="/marketing/hero/photo-11.png" alt="" width={193} height={194} className="absolute object-cover" style={{left: 947+28, top: 582}} />
              <Image src="/marketing/hero/photo-12.png" alt="" width={221} height={276} className="absolute rounded-[16px] object-cover" style={{left: 611, top: 423}} />
              <Image src="/marketing/hero/photo-13.png" alt="" width={283} height={234} className="absolute rounded-[16px] object-cover" style={{left: 376, top: 445}} />

              {/* Scribbles */}
              <Image src="/marketing/hero/scribble-01.png" alt="" width={208} height={57} className="absolute" style={{left: 63+28, top: 570}} />
              <Image src="/marketing/hero/scribble-02.png" alt="" width={111} height={129} className="absolute" style={{left: 740+28, top: 18}} />
              <Image src="/marketing/hero/scribble-03.png" alt="" width={35} height={109} className="absolute" style={{left: 356+28, top: 347}} />
              <Image src="/marketing/hero/scribble-04.png" alt="" width={110} height={116} className="absolute" style={{left: 1058+28, top: 477}} />
              <Image src="/marketing/hero/scribble-05.png" alt="" width={441} height={161} className="absolute" style={{left: 0, top: 616}} />
            </div>
            
            {/* Mobile Fallback for Collage */}
            <div className="lg:hidden flex flex-wrap justify-center gap-4 px-6 mt-10">
               <Image src="/marketing/hero/photo-04.png" alt="" width={240} height={427} className="rounded-[16px]" />
               <Image src="/marketing/hero/photo-05.png" alt="" width={254} height={320} className="rounded-[16px]" />
            </div>

            {/* Buttons */}
            <div className="flex gap-[20px] mt-[10px] lg:mt-[0px] lg:absolute lg:top-[777px] lg:left-[686px] z-20">
              <Link href="/signup" className="px-[19px] py-[10px] bg-[#FF6100] text-white rounded-[10px] flex items-center justify-center font-host font-medium text-[18px]">Buy Credits</Link>
              <Link href="#how-it-works" className="text-[#313131] underline font-host font-medium text-[18px] flex items-center justify-center px-[19px] py-[10px]">See how it works</Link>
            </div>
          </section>

          {/* Intro Text */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[1119px] lg:left-[100px] z-10 mt-16 lg:mt-0">
             <h1 className="text-[40px] lg:text-[60px] font-extrabold text-[#313131] max-w-[708px] leading-[1em]">
               Upload event photos. Let your attendees claim them free.
             </h1>
             <Image src="/marketing/hero/scribble-06.png" alt="" width={214} height={210} className="hidden lg:block absolute left-[116px] top-[47px] -z-10" />
          </section>

          {/* How it works cards */}
          <section id="how-it-works" className="px-6 lg:px-0 lg:absolute lg:top-[1354px] lg:left-[242px] z-20 mt-16 lg:mt-0 flex flex-col lg:flex-row gap-[39px]">
             {/* Card 1 */}
             <div className="w-full lg:w-[388px] h-[435px] relative rounded-[16px] overflow-hidden shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)] bg-white flex justify-center">
                 <Image src="/marketing/features/photo-04.png" alt="" width={390} height={490} className="absolute left-[-35px] top-[-78px] object-cover opacity-20" />
                 <h2 className="text-[30px] font-extrabold text-[#313131] mt-[155px] text-center z-10 leading-[1em] max-w-[187px]">You buy credits</h2>
             </div>
             {/* Card 2 */}
             <div className="w-full lg:w-[388px] h-[435px] relative rounded-[16px] overflow-hidden shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)] bg-white flex justify-center">
                 <Image src="/marketing/features/photo-05.png" alt="" width={390} height={490} className="absolute left-[-35px] top-[-78px] object-cover" />
                 <div className="absolute inset-0 bg-black bg-opacity-20"></div>
                 <h2 className="text-[30px] font-extrabold text-white mt-[155px] text-center z-10 leading-[1em] max-w-[187px]">You upload<br/>the photos</h2>
             </div>
             {/* Card 3 */}
             <div className="w-full lg:w-[388px] h-[435px] relative rounded-[16px] overflow-hidden shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)] bg-white flex justify-center">
                 <Image src="/marketing/features/photo-06.png" alt="" width={1200} height={1499} className="absolute left-[-559px] top-[-621px] object-cover opacity-20" />
                 <h2 className="text-[30px] font-extrabold text-[#313131] mt-[155px] text-center z-10 leading-[1em] max-w-[191px]">Attendees download free</h2>
             </div>
          </section>

          {/* Central Texts */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[1959px] lg:left-[510px] z-10 mt-16 lg:mt-0 flex flex-col items-center w-full lg:w-auto">
             <h2 className="text-[40px] lg:text-[60px] font-extrabold text-[#313131] text-center max-w-[708px] leading-[1em]">
               Built around <span className="text-[#FF6100]">one job:</span> getting photos to the right person
             </h2>
             <Image src="/marketing/hero/scribble-06.png" alt="" width={214} height={210} className="hidden lg:block absolute left-[140px] top-[51px] -z-10" />
          </section>

          <section className="px-6 lg:px-0 lg:absolute lg:top-[2161px] lg:left-[615px] z-10 mt-8 lg:mt-0 flex justify-center w-full lg:w-auto">
             <p className="text-[18px] font-medium text-[#313131] text-center max-w-[502px]">
               Studio is separate from the main FindMyShots marketplace. It's just for the organizer side of uploading.
             </p>
          </section>

          {/* Dashboard Image */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[2283px] lg:left-[281px] z-10 mt-16 lg:mt-0 w-full lg:w-auto flex justify-center relative">
             <Image src="/marketing/demo/my-albums.png" alt="Dashboard" width={1165} height={748} className="rounded-[40px] border-[25px] border-black shadow-xl" />
             
             {/* Floating Tags (Desktop only for exact positioning) */}
             <div className="hidden lg:flex absolute top-[98px] left-[-140px] px-[19px] py-[10px] bg-[#FF6100] text-white rounded-full text-[18px] shadow-lg">Personalize</div>
             <div className="hidden lg:flex absolute top-[257px] left-[-42px] px-[19px] py-[10px] bg-[#FF6100] text-white rounded-full text-[18px] shadow-lg items-center gap-2">Buy Credits</div>
             <div className="hidden lg:flex absolute top-[421px] left-[-139px] px-[19px] py-[10px] bg-[#FF6100] text-white rounded-full text-[18px] shadow-lg">Upload</div>
             
             <div className="hidden lg:flex absolute top-[98px] right-[-33px] px-[19px] py-[10px] bg-[#FF6100] text-white rounded-full text-[18px] shadow-lg">Organize</div>
             <div className="hidden lg:flex absolute top-[257px] right-[48px] px-[19px] py-[10px] bg-[#FF6100] text-white rounded-full text-[18px] shadow-lg">Share Link</div>
             <div className="hidden lg:flex absolute top-[421px] right-[-33px] px-[19px] py-[10px] bg-[#FF6100] text-white rounded-full text-[18px] shadow-lg">Download Free</div>
          </section>

          {/* Orange Features Block */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[2901px] lg:left-[0px] z-10 mt-16 lg:mt-0 w-full">
             <div className="w-full lg:w-[1728px] lg:h-[610px] bg-[#FF6100] lg:rounded-[50px] relative mx-auto flex flex-col lg:flex-row justify-center items-center py-16 lg:py-0 gap-[60px] lg:gap-0">
                
                {/* Feature 1 */}
                <div className="relative w-[304px] h-[350px] lg:absolute lg:left-[220px] lg:top-[106px]">
                   {/* Image Card (Behind) */}
                   <div className="absolute top-[48px] left-[0px] w-[304px] h-[350px] bg-white rounded-[16px] overflow-hidden shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)]">
                       <Image src="/marketing/features/photo-01.png" alt="" width={465} height={620} className="absolute left-[-114px] top-[-61px] max-w-none" />
                   </div>
                   {/* Text Card (Front) */}
                   <div className="absolute top-[26px] left-[46px] w-[304px] h-[350px] bg-white rounded-[16px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)] p-[29px] flex flex-col">
                       <span className="text-[40px] font-extrabold text-[rgba(49,49,49,0.5)] leading-none">01</span>
                       <h3 className="text-[40px] font-extrabold text-[#FF6100] mt-[16px] leading-[1em]">Credits, not subscriptions</h3>
                       <p className="text-[20px] text-[#313131] mt-[14px]">Buy a block of credits and draw them down per photo. Nothing expires between events.</p>
                   </div>
                </div>

                {/* Feature 2 */}
                <div className="relative w-[304px] h-[350px] lg:absolute lg:left-[663px] lg:top-[106px]">
                   <div className="absolute top-[48px] left-[0px] w-[304px] h-[350px] bg-white rounded-[16px] overflow-hidden shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)]">
                       <Image src="/marketing/features/photo-02.png" alt="" width={338} height={450} className="absolute left-[-17px] top-[-50px] max-w-none" />
                   </div>
                   <div className="absolute top-[26px] left-[49px] w-[304px] h-[350px] bg-white rounded-[16px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)] p-[29px] flex flex-col">
                       <span className="text-[40px] font-extrabold text-[rgba(49,49,49,0.5)] leading-none">02</span>
                       <h3 className="text-[40px] font-extrabold text-[#FF6100] mt-[16px] leading-[1em]">One dashboard per event</h3>
                       <p className="text-[20px] text-[#313131] mt-[14px]">Track upload volume, credit balance, and match rate for every event.</p>
                   </div>
                </div>

                {/* Feature 3 */}
                <div className="relative w-[304px] h-[350px] lg:absolute lg:left-[1109px] lg:top-[106px]">
                   <div className="absolute top-[40px] left-[0px] w-[304px] h-[350px] bg-white rounded-[16px] overflow-hidden shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)]">
                       <Image src="/marketing/features/photo-03.png" alt="" width={307} height={460} className="absolute left-[-3px] top-[-80px] max-w-none" />
                   </div>
                   <div className="absolute top-[26px] left-[48px] w-[304px] h-[350px] bg-white rounded-[16px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.1)] p-[29px] flex flex-col">
                       <span className="text-[40px] font-extrabold text-[rgba(49,49,49,0.5)] leading-none">03</span>
                       <h3 className="text-[40px] font-extrabold text-[#FF6100] mt-[16px] leading-[1em]">Attendees never pay</h3>
                       <p className="text-[20px] text-[#313131] mt-[14px]">Your credits are what make the download free on the attendee-facing app.</p>
                   </div>
                </div>

             </div>
          </section>

          {/* Customization Section */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[3702px] lg:left-[98px] z-10 mt-16 lg:mt-0 w-full flex flex-col lg:flex-row gap-[98px] items-center">
             <div className="w-full lg:w-[619px] flex flex-col gap-[33px]">
                <div className="relative">
                  <h2 className="text-[40px] lg:text-[60px] font-extrabold text-[#313131] leading-[1em]">Every album looks like <span className="text-[#FF6100]">your event,</span> not ours</h2>
                  <p className="text-[18px] font-medium text-[#313131] mt-[11px]">Set a font and a theme per album before you publish it. Attendees see your event's identity — not a generic template.</p>
                  <Image src="/marketing/hero/scribble-06.png" alt="" width={214} height={210} className="hidden lg:block absolute left-[153px] top-[-74px] -z-10" />
                </div>
                
                {/* Fonts */}
                <div className="flex flex-col gap-[12px]">
                   <span className="text-[18px] font-medium text-[#313131]">Album Font</span>
                   <div className="flex flex-col gap-[11px]">
                       <div className="flex flex-wrap gap-[19px]">
                           <div className="w-[192px] h-[72px] bg-white rounded-[10px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.25)] flex items-center px-[18px] gap-[14px]">
                               <span className="text-[30px] font-host text-[#313131]">Aa</span>
                               <span className="text-[18px] font-host text-[rgba(0,0,0,0.6)]">Host Grotesk</span>
                           </div>
                           <div className="w-[192px] h-[72px] bg-white rounded-[10px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.25)] flex items-center px-[18px] gap-[14px]">
                               <span className="text-[30px] font-[Honfleur] font-black text-[#313131] mt-2">Aa</span>
                               <span className="text-[18px] font-host text-[rgba(0,0,0,0.6)]">Honfleur</span>
                           </div>
                           <div className="w-[192px] h-[72px] bg-white rounded-[10px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.25)] flex items-center px-[18px] gap-[14px]">
                               <span className="text-[30px] font-[High Tower Text] text-[#313131]">Aa</span>
                               <span className="text-[18px] font-host text-[rgba(0,0,0,0.6)]">High Tower</span>
                           </div>
                       </div>
                       <div className="flex flex-wrap gap-[19px]">
                           <div className="w-[192px] h-[72px] bg-white rounded-[10px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.25)] flex items-center px-[18px] gap-[14px]">
                               <span className="text-[30px] font-[Hubballi] text-[#313131]">Aa</span>
                               <span className="text-[18px] font-host text-[rgba(0,0,0,0.6)]">Hubbali</span>
                           </div>
                           <div className="w-[192px] h-[72px] bg-white rounded-[10px] border-[3px] border-[#FF6100] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.25)] flex items-center px-[18px] gap-[14px]">
                               <span className="text-[30px] font-[Hi Melody] text-[#313131]">Aa</span>
                               <span className="text-[18px] font-host text-[rgba(0,0,0,0.6)]">Hi Melody</span>
                           </div>
                           <div className="w-[192px] h-[72px] bg-white rounded-[10px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.25)] flex items-center px-[18px] gap-[14px]">
                               <span className="text-[30px] font-[Helvetica LT Std] font-bold text-[#313131]">Aa</span>
                               <span className="text-[18px] font-host text-[rgba(0,0,0,0.6)]">Helvetica</span>
                           </div>
                       </div>
                   </div>
                </div>

                {/* Colors */}
                <div className="flex flex-col gap-[2px]">
                   <span className="text-[18px] font-medium text-[#313131]">Theme Color</span>
                   <div className="flex flex-wrap gap-[19px] mt-2">
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#E53935] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#FF6100] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#FED448] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#31B85C] border-[3px] border-[#FF6100] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)] relative overflow-hidden">
                           <Image src="/marketing/demo/swatch-overlay-01.png" alt="" width={101} height={126} className="absolute left-[-19px] top-[-58px] opacity-50 mix-blend-overlay max-w-none" />
                       </div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#EE08E7] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)] relative overflow-hidden">
                           <Image src="/marketing/demo/swatch-overlay-02.png" alt="" width={100} height={56} className="absolute left-[-22px] top-[-6px] opacity-50 mix-blend-overlay max-w-none" />
                       </div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#357992] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#535862] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#7C57FF] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <div className="w-[44px] h-[44px] rounded-[10px] bg-[#000000] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]"></div>
                       <Image src="/marketing/demo/swatch-gradient.svg" alt="" width={44} height={44} className="rounded-[10px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.1)]" />
                   </div>
                </div>
             </div>
             
             {/* Approved Image */}
             <div className="w-full lg:w-auto relative lg:left-[147px] mt-10 lg:mt-0">
                <Image src="/marketing/demo/approved.png" alt="Album" width={1128} height={642} className="rounded-[25px] border-[25px] border-black max-w-full lg:max-w-none" />
             </div>
          </section>

          {/* Pricing Header */}
          <section id="pricing" className="px-6 lg:px-0 lg:absolute lg:top-[4679px] lg:left-[104px] z-10 mt-24 lg:mt-0 w-full flex flex-col gap-[12px]">
             <h2 className="text-[40px] lg:text-[60px] font-extrabold text-[#313131] leading-[1em]">Credit Packages</h2>
             <p className="text-[18px] font-medium text-[#313131]">1 credit uploads 1 photo. Pick a package below.</p>
             <div className="inline-flex mt-1">
                 <div className="px-[19px] py-[3px] bg-[#FF6100] rounded-full text-white text-[16px] font-host inline-block">
                     <span className="opacity-60">Rate: </span>$0.05 <span className="opacity-60">per credit</span>
                 </div>
             </div>
          </section>

          {/* Pricing Cards */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[4883px] lg:left-[104px] z-10 mt-10 lg:mt-0 w-full flex flex-col lg:flex-row gap-[42px]">
             
             {/* 3000 */}
             <div className="w-full lg:w-[350px] h-[426px] bg-white rounded-[40px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.2)] p-[30px] flex flex-col relative">
                <h3 className="text-[20px] font-host font-normal text-[#313131]">Credits</h3>
                <div className="text-[50px] font-heavitas text-[#313131] mt-4 mb-2">3,000</div>
                <div className="text-[20px] text-[#313131]">$150 total</div>
                <hr className="border-[#313131] border-[1px] my-5" />
                <div className="text-[20px] text-[#313131] whitespace-pre-line leading-relaxed mb-auto">
                   - ~3,000 photos uploaded{"\n"}
                   - Fits a single-day event{"\n"}
                   - Credits never expire
                </div>
                <Image src="/icons/shopping-bag.svg" alt="" width={54} height={54} className="absolute right-[46px] top-[58px]" />
                <div className="flex flex-col gap-2 w-full mt-4">
                   <Link href="/signup" className="w-[239px] h-[48px] bg-[#FF6100] text-white rounded-[10px] flex items-center justify-center text-[20px] font-medium mx-auto">Select Option</Link>
                   <div className="text-[18px] font-medium text-[rgba(49,49,49,0.6)] text-center">No Expiration • One time pay</div>
                </div>
             </div>

             {/* 5000 */}
             <div className="w-full lg:w-[350px] h-[426px] bg-white rounded-[40px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.2)] p-[30px] flex flex-col relative">
                <h3 className="text-[20px] font-host font-normal text-[#313131]">Credits</h3>
                <div className="text-[50px] font-heavitas text-[#313131] mt-4 mb-2">5,000</div>
                <div className="text-[20px] text-[#313131]">$250 total</div>
                <hr className="border-[#313131] border-[1px] my-5" />
                <div className="text-[20px] text-[#313131] whitespace-pre-line leading-relaxed mb-auto">
                   - ~5,000 photos uploaded{"\n"}
                   - Comfortable buffer for reshoots{"\n"}
                   - Credits never expire
                </div>
                <Image src="/icons/calendar-heart.svg" alt="" width={54} height={54} className="absolute right-[46px] top-[58px]" />
                <div className="flex flex-col gap-2 w-full mt-4">
                   <Link href="/signup" className="w-[239px] h-[48px] bg-[#FF6100] text-white rounded-[10px] flex items-center justify-center text-[20px] font-medium mx-auto">Select Option</Link>
                   <div className="text-[18px] font-medium text-[rgba(49,49,49,0.6)] text-center">No Expiration • One time pay</div>
                </div>
             </div>

             {/* 10000 */}
             <div className="w-full lg:w-[350px] h-[426px] bg-white rounded-[40px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.2)] p-[30px] flex flex-col relative">
                <h3 className="text-[20px] font-host font-normal text-[#313131]">Credits</h3>
                <div className="text-[50px] font-heavitas text-[#313131] mt-4 mb-2">10,000</div>
                <div className="text-[20px] text-[#313131]">$500 total</div>
                <hr className="border-[#313131] border-[1px] my-5" />
                <div className="text-[20px] text-[#313131] whitespace-pre-line leading-relaxed mb-auto">
                   - ~10,000 photos uploaded{"\n"}
                   - Good for multi-day events{"\n"}
                   - Credits never expire
                </div>
                <Image src="/icons/ticket.svg" alt="" width={54} height={54} className="absolute right-[46px] top-[58px]" />
                <div className="flex flex-col gap-2 w-full mt-4">
                   <Link href="/signup" className="w-[239px] h-[48px] bg-[#FF6100] text-white rounded-[10px] flex items-center justify-center text-[20px] font-medium mx-auto">Select Option</Link>
                   <div className="text-[18px] font-medium text-[rgba(49,49,49,0.6)] text-center">No Expiration • One time pay</div>
                </div>
             </div>

             {/* 15000 */}
             <div className="w-full lg:w-[350px] h-[426px] bg-white rounded-[40px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.2)] p-[30px] flex flex-col relative">
                <h3 className="text-[20px] font-host font-normal text-[#313131]">Credits</h3>
                <div className="text-[50px] font-heavitas text-[#313131] mt-4 mb-2">15,000</div>
                <div className="text-[20px] text-[#313131]">$750 total</div>
                <hr className="border-[#313131] border-[1px] my-5" />
                <div className="text-[20px] text-[#313131] whitespace-pre-line leading-relaxed mb-auto">
                   - ~15,000 photos uploaded{"\n"}
                   - Built for large-scale events{"\n"}
                   - Credits never expire
                </div>
                <Image src="/icons/gift.svg" alt="" width={54} height={54} className="absolute right-[46px] top-[58px]" />
                <div className="flex flex-col gap-2 w-full mt-4">
                   <Link href="/signup" className="w-[239px] h-[48px] bg-[#FF6100] text-white rounded-[10px] flex items-center justify-center text-[20px] font-medium mx-auto">Select Option</Link>
                   <div className="text-[18px] font-medium text-[rgba(49,49,49,0.6)] text-center">No Expiration • One time pay</div>
                </div>
             </div>

          </section>

          {/* Need Fewer/More */}
          <section className="px-6 lg:px-0 lg:absolute lg:top-[5381px] lg:left-[104px] z-10 mt-16 lg:mt-0 w-full lg:w-[1526px]">
             <div className="w-full h-[135px] bg-white rounded-[16px] shadow-[0px_0px_30px_0px_rgba(0,0,0,0.2)] flex items-center justify-between px-[42px]">
                 <div className="flex items-center gap-[22px]">
                     <Image src="/icons/images.svg" alt="" width={54} height={54} />
                     <div className="text-[20px] lg:text-[30px] font-extrabold text-[#313131] leading-[1em]">
                        Need <span className="text-[#FF6100]">fewer</span> than 3,000 or <span className="text-[#FF6100]">more</span> than 15,000 credits?
                     </div>
                 </div>
                 <Link href="mailto:support@findmyshots.com" className="px-[19px] py-[10px] bg-[#FF6100] text-white rounded-[10px] text-[20px] font-medium shrink-0">
                    Contact Us
                 </Link>
             </div>
          </section>

        </main>
        
        {/* Footer */}
        <footer className="w-full max-w-[1728px] mx-auto px-6 lg:px-[104px] lg:absolute lg:top-[5660px] pb-10 flex flex-col lg:flex-row justify-between items-center text-[#313131]">
           <span className="text-[25px] font-extrabold tracking-[0.02em]">findmyshots</span>
           <div className="flex gap-[30px] text-[20px] mt-4 lg:mt-0">
               <Link href="/about" className="hover:text-[#FF6100]">About</Link>
               <Link href="/privacy" className="hover:text-[#FF6100]">Privacy</Link>
               <span className="text-[#797979]">Made by Symph</span>
           </div>
        </footer>
      </div>
    </div>
  );
}
"""
    with open("/home/openclaw/projects/.worktrees/fms-studio/bug__landing-page-pixel-perfect/frontend/src/app/page.tsx", "w") as f:
        f.write(page)

if __name__ == "__main__":
    render()
