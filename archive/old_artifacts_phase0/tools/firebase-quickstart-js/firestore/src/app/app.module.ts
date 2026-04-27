/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { NgModule } from '@angular/core';
import { initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { connectAuthEmulator, getAuth, provideAuth } from '@angular/fire/auth';
import { getFirestore, provideFirestore } from '@angular/fire/firestore';
import { getFunctions, provideFunctions } from '@angular/fire/functions';
import { getStorage, provideStorage } from '@angular/fire/storage';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatOptionModule } from '@angular/material/core';
import { MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatToolbarModule } from '@angular/material/toolbar';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { connectFirestoreEmulator } from '@firebase/firestore';
import { projectConfig } from '../environments/environment.default';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { FilterDialogComponent } from './filter-dialog/filter-dialog.component';
import { HomepageComponent } from './homepage/homepage.component';
import { DefaultHomepageFirestore, HomepageFirestore } from './homepage/hompage.service';
import { RestaurantCardComponent } from './restaurant-card/restaurant-card.component';
import { RestuarantPageComponent } from './restuarant-page/restuarant-page.component';
import { ReviewListComponent } from './review-list/review-list.component';
import { SignInModalComponent } from './sign-in-modal/sign-in-modal.component';
import { SubmitReviewModalComponent } from './submit-review-modal/submit-review-modal.component';

@NgModule({
  declarations: [
    AppComponent,
    HomepageComponent,
    RestuarantPageComponent,
    RestaurantCardComponent,
    ReviewListComponent,
    FilterDialogComponent,
    SubmitReviewModalComponent,
    SignInModalComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MatSlideToggleModule,
    MatCardModule,
    FlexLayoutModule,
    MatToolbarModule,
    MatIconModule,
    MatDividerModule,
    MatDialogModule,
    MatSelectModule,
    MatFormFieldModule,
    MatOptionModule,
    MatInputModule,
    MatButtonModule,
    BrowserAnimationsModule,
    provideFirebaseApp(() => initializeApp(projectConfig)),
    FormsModule,
    provideAuth(() => {
      const auth = getAuth();
      if (auth.app.options.projectId!.indexOf('demo') === 0)
        connectAuthEmulator(auth, 'http://127.0.0.1:9099');

      return auth;
    }),
    provideFirestore(() => {
      const firestore = getFirestore();

      if (firestore.app.options.projectId!.indexOf('demo') === 0)
        connectFirestoreEmulator(firestore, '127.0.0.1', 8080);

      return firestore;
    }),
    provideFunctions(() => getFunctions()),
    provideStorage(() => getStorage()),
  ],
  providers: [{ provide: HomepageFirestore, useClass: DefaultHomepageFirestore }],
  bootstrap: [AppComponent],
})
export class AppModule {}
